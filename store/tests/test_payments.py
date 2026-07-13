import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from store.models import CartItem, Order, OrderItem, Product
from store.payments import YooKassaError, build_payment_payload, validate_payment


PAYMENT_SETTINGS = {
    "YOOKASSA_SHOP_ID": "test-shop",
    "YOOKASSA_SECRET_KEY": "test-secret",
    "YOOKASSA_SIMULATION": False,
    "YOOKASSA_TEST_MODE": False,
    "YOOKASSA_RECEIPTS_ENABLED": False,
}


class YooKassaPaymentTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="test-password",
        )
        self.order = Order.objects.create(
            user=self.user,
            full_name="Иван Иванов",
            phone="+79990000000",
            address="Москва",
            email="buyer@example.com",
            payment_method=Order.PAYMENT_METHOD_CARD,
            total_price=2500,
        )
        OrderItem.objects.create(
            order=self.order,
            product_title="Букет роз",
            price=2500,
            quantity=1,
            image_url="https://example.com/rose.jpg",
        )

    def payment(self, *, status="pending", payment_id="payment-1", value="2500.00"):
        return {
            "id": payment_id,
            "status": status,
            "amount": {"value": value, "currency": "RUB"},
            "metadata": {
                "order_id": str(self.order.id),
                "user_id": str(self.user.id),
            },
            "confirmation": {
                "type": "redirect",
                "confirmation_url": "https://yookassa.example/confirm",
            },
        }

    @override_settings(**PAYMENT_SETTINGS)
    def test_payload_uses_selected_card_method(self):
        payload = build_payment_payload(self.order, "https://shop.example/return")

        self.assertEqual(payload["payment_method_data"], {"type": "bank_card"})
        self.assertEqual(payload["amount"], {"value": "2500.00", "currency": "RUB"})
        self.assertEqual(payload["metadata"]["order_id"], str(self.order.id))

    @override_settings(**PAYMENT_SETTINGS)
    def test_payload_uses_selected_sbp_method(self):
        self.order.payment_method = Order.PAYMENT_METHOD_SBP

        payload = build_payment_payload(self.order, "https://shop.example/return")

        self.assertEqual(payload["payment_method_data"], {"type": "sbp"})

    @override_settings(**{**PAYMENT_SETTINGS, "YOOKASSA_TEST_MODE": True})
    def test_test_shop_rejects_sbp(self):
        self.order.payment_method = Order.PAYMENT_METHOD_SBP

        with self.assertRaises(YooKassaError):
            build_payment_payload(self.order, "https://shop.example/return")

    @override_settings(
        **{
            **PAYMENT_SETTINGS,
            "YOOKASSA_RECEIPTS_ENABLED": True,
            "YOOKASSA_VAT_CODE": 1,
        }
    )
    def test_receipt_contains_order_items_and_customer(self):
        payload = build_payment_payload(self.order, "https://shop.example/return")

        self.assertEqual(payload["receipt"]["customer"]["email"], "buyer@example.com")
        self.assertEqual(payload["receipt"]["items"][0]["quantity"], 1)
        self.assertEqual(payload["receipt"]["items"][0]["vat_code"], 1)

    def test_validation_rejects_changed_amount(self):
        with self.assertRaises(YooKassaError):
            validate_payment(self.order, self.payment(value="1.00"))

    @override_settings(**PAYMENT_SETTINGS)
    @patch("store.views.fetch_payment")
    def test_webhook_verifies_payment_and_marks_order_paid(self, fetch_payment_mock):
        self.order.provider_payment_id = "payment-1"
        self.order.save(update_fields=["provider_payment_id"])
        fetch_payment_mock.return_value = self.payment(status="succeeded")
        payload = {"event": "payment.succeeded", "object": {"id": "payment-1"}}

        response = self.client.post(
            reverse("yookassa_webhook"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertIsNotNone(self.order.paid_at)

    @override_settings(**PAYMENT_SETTINGS)
    @patch("store.views.fetch_payment")
    def test_webhook_rejects_payment_with_wrong_amount(self, fetch_payment_mock):
        self.order.provider_payment_id = "payment-1"
        self.order.save(update_fields=["provider_payment_id"])
        fetch_payment_mock.return_value = self.payment(status="succeeded", value="1.00")
        payload = {"event": "payment.succeeded", "object": {"id": "payment-1"}}

        response = self.client.post(
            reverse("yookassa_webhook"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 503)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_PENDING)

    @override_settings(**PAYMENT_SETTINGS)
    def test_return_page_is_limited_to_order_owner(self):
        other_user = get_user_model().objects.create_user(username="other", password="test-password")
        self.client.force_login(other_user)

        response = self.client.get(reverse("yookassa_return"), {"order_id": self.order.id})

        self.assertEqual(response.status_code, 404)

    @override_settings(**PAYMENT_SETTINGS)
    @patch("store.views.fetch_payment")
    def test_existing_pending_payment_is_reused(self, fetch_payment_mock):
        self.order.provider_payment_id = "payment-1"
        self.order.save(update_fields=["provider_payment_id"])
        fetch_payment_mock.return_value = self.payment()
        self.client.force_login(self.user)

        response = self.client.get(reverse("start_payment", args=[self.order.id]))

        self.assertRedirects(
            response,
            "https://yookassa.example/confirm",
            fetch_redirect_response=False,
        )
        fetch_payment_mock.assert_called_once_with("payment-1")

    @override_settings(**PAYMENT_SETTINGS)
    def test_cash_order_does_not_call_yookassa_and_clears_cart(self):
        self.order.payment_method = Order.PAYMENT_METHOD_CASH
        self.order.save(update_fields=["payment_method"])
        product = Product.objects.create(
            title="Ромашки",
            price=1000,
            image_url="https://example.com/daisy.jpg",
        )
        CartItem.objects.create(user=self.user, product=product)
        self.client.force_login(self.user)

        with patch("store.views.create_payment") as create_payment_mock:
            response = self.client.get(reverse("start_payment", args=[self.order.id]))

        self.assertRedirects(response, reverse("index"), fetch_redirect_response=False)
        create_payment_mock.assert_not_called()
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
