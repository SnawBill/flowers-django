import base64
import json
import uuid
from decimal import Decimal, InvalidOperation
from urllib import error as urllib_error
from urllib import request as urllib_request

from django.conf import settings


YOOKASSA_API_URL = "https://api.yookassa.ru/v3"
PAYMENT_METHOD_TYPES = {
    "card": "bank_card",
    "sbp": "sbp",
}


class YooKassaError(Exception):
    """Raised when a request or response from YooKassa cannot be trusted."""


def yookassa_enabled():
    return bool(settings.YOOKASSA_SHOP_ID and settings.YOOKASSA_SECRET_KEY)


def _authorization_header():
    credentials = f"{settings.YOOKASSA_SHOP_ID}:{settings.YOOKASSA_SECRET_KEY}"
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("ascii")
    return f"Basic {encoded}"


def _request(path, *, method="GET", payload=None, idempotence_key=None):
    headers = {"Authorization": _authorization_header()}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if idempotence_key:
        headers["Idempotence-Key"] = idempotence_key

    request = urllib_request.Request(
        f"{YOOKASSA_API_URL}{path}",
        data=data,
        method=method,
        headers=headers,
    )
    try:
        with urllib_request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib_error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise YooKassaError(details or f"YooKassa HTTP {exc.code}") from exc
    except (urllib_error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise YooKassaError(str(exc)) from exc


def _receipt_payload(order):
    if not settings.YOOKASSA_RECEIPTS_ENABLED:
        return None

    email = order.email or order.user.email
    if not email:
        raise YooKassaError("Для отправки электронного чека требуется email покупателя.")

    return {
        "customer": {
            "full_name": order.full_name,
            "email": email,
        },
        "items": [
            {
                "description": item.product_title[:128],
                "quantity": item.quantity,
                "amount": {
                    "value": f"{item.price:.2f}",
                    "currency": "RUB",
                },
                "vat_code": settings.YOOKASSA_VAT_CODE,
                "payment_mode": "full_payment",
                "payment_subject": "commodity",
            }
            for item in order.items.all()
        ],
    }


def build_payment_payload(order, return_url):
    if settings.YOOKASSA_TEST_MODE and order.payment_method == "sbp":
        raise YooKassaError("СБП недоступна в тестовом магазине ЮKassa.")
    payment_method_type = PAYMENT_METHOD_TYPES.get(order.payment_method)
    if not payment_method_type:
        raise YooKassaError("Выбранный способ оплаты не поддерживается ЮKassa.")

    payload = {
        "amount": {
            "value": f"{order.total_price:.2f}",
            "currency": "RUB",
        },
        "capture": True,
        "payment_method_data": {"type": payment_method_type},
        "confirmation": {
            "type": "redirect",
            "return_url": return_url,
        },
        "description": f"Оплата заказа #{order.id}",
        "metadata": {
            "order_id": str(order.id),
            "user_id": str(order.user_id),
        },
    }
    receipt = _receipt_payload(order)
    if receipt:
        payload["receipt"] = receipt
    return payload


def payment_idempotence_key(order):
    source = f"{settings.SECRET_KEY}:yookassa:order:{order.id}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, source))


def create_payment(order, return_url):
    return _request(
        "/payments",
        method="POST",
        payload=build_payment_payload(order, return_url),
        idempotence_key=payment_idempotence_key(order),
    )


def fetch_payment(payment_id):
    return _request(f"/payments/{payment_id}")


def validate_payment(order, payment):
    payment_id = str(payment.get("id", ""))
    if not payment_id:
        raise YooKassaError("ЮKassa вернула платеж без идентификатора.")
    if order.provider_payment_id and payment_id != order.provider_payment_id:
        raise YooKassaError("Идентификатор платежа не соответствует заказу.")

    metadata = payment.get("metadata") or {}
    if str(metadata.get("order_id", "")) != str(order.id):
        raise YooKassaError("Платеж связан с другим заказом.")
    if str(metadata.get("user_id", "")) != str(order.user_id):
        raise YooKassaError("Платеж связан с другим пользователем.")

    amount = payment.get("amount") or {}
    try:
        value = Decimal(str(amount.get("value")))
    except (InvalidOperation, TypeError):
        raise YooKassaError("ЮKassa вернула некорректную сумму платежа.") from None
    if amount.get("currency") != "RUB" or value != Decimal(order.total_price):
        raise YooKassaError("Сумма платежа не соответствует сумме заказа.")
    return payment
