from django.test import SimpleTestCase, override_settings
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
    DELIVERY_PRICE="500",
    DELIVERY_TIME="до 2 часов",
)
class LegalPagesTests(SimpleTestCase):
    def test_public_information_pages_are_available(self):
        for route_name in ("contacts", "delivery", "offer", "privacy", "requisites"):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)

    def test_requisites_page_contains_seller_information(self):
        response = self.client.get(reverse("requisites"))

        self.assertContains(response, "Иванов Иван Иванович")
        self.assertContains(response, "000000000000")
        self.assertContains(response, "Уссурийск")

    def test_footer_contains_required_links(self):
        response = self.client.get(reverse("contacts"))

        self.assertContains(response, reverse("delivery"))
        self.assertContains(response, reverse("offer"))
        self.assertContains(response, reverse("privacy"))
        self.assertContains(response, reverse("requisites"))
