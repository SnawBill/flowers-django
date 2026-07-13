from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


TEST_STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


@override_settings(
    STORAGES=TEST_STORAGES,
    SELLER_NAME="Иванов Иван Иванович",
    SELLER_INN="000000000000",
    SELLER_PHONE="+7 900 000-00-00",
    SELLER_EMAIL="seller@example.com",
    SELLER_CITY="Уссурийск",
    SELLER_ADDRESS="г. Уссурийск, ул. Тестовая, д. 1",
    DELIVERY_PRICE="500",
    DELIVERY_TIME="до 2 часов",
)
class LegalPagesTests(TestCase):
    def test_public_information_pages_are_available(self):
        for route_name in ("contacts", "delivery", "offer", "privacy", "requisites"):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)

    def test_requisites_page_contains_seller_information(self):
        response = self.client.get(reverse("requisites"))

        self.assertContains(response, "Иванов Иван Иванович")
        self.assertContains(response, "000000000000")
        self.assertContains(response, "г. Уссурийск, ул. Тестовая, д. 1")
        self.assertContains(response, "+7 900 000-00-00")
        self.assertContains(response, "seller@example.com")

    def test_footer_contains_required_links(self):
        response = self.client.get(reverse("contacts"))

        self.assertContains(response, reverse("delivery"))
        self.assertContains(response, reverse("offer"))
        self.assertContains(response, reverse("privacy"))
        self.assertContains(response, reverse("requisites"))

    def test_contacts_page_contains_business_contacts(self):
        response = self.client.get(reverse("contacts"))

        self.assertContains(response, "+7 900 000-00-00")
        self.assertContains(response, "seller@example.com")
        self.assertContains(response, "г. Уссурийск, ул. Тестовая, д. 1")

    def test_business_contacts_are_not_duplicated_on_homepage(self):
        response = self.client.get(reverse("index"))

        self.assertNotContains(response, "+7 900 000-00-00")
        self.assertNotContains(response, "seller@example.com")


@override_settings(
    STORAGES=TEST_STORAGES,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="site@example.com",
    CONTACT_EMAIL="owner@example.com",
    SELLER_CITY="Уссурийск",
)
class ContactFormTests(TestCase):
    payload = {
        "name": "Анна",
        "email": "anna@example.com",
        "subject": "Доставка букета",
        "message": "Подскажите доступное время доставки.",
        "website": "",
    }

    def test_contact_form_sends_email_to_owner(self):
        response = self.client.post(reverse("contacts"), self.payload)

        self.assertRedirects(response, reverse("contacts"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["anna@example.com"])
        self.assertIn("Доставка букета", mail.outbox[0].subject)

    def test_honeypot_blocks_spam(self):
        payload = {**self.payload, "website": "https://spam.example"}

        response = self.client.post(reverse("contacts"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mail.outbox, [])

    def test_second_message_is_rate_limited(self):
        self.client.post(reverse("contacts"), self.payload)
        response = self.client.post(reverse("contacts"), self.payload)

        self.assertRedirects(response, reverse("contacts"))
        self.assertEqual(len(mail.outbox), 1)
