import re

from django.conf import settings


def site_information(request):
    phone_digits = re.sub(r"\D", "", settings.SELLER_PHONE)
    if len(phone_digits) == 11 and phone_digits.startswith("8"):
        phone_digits = f"7{phone_digits[1:]}"

    return {
        "seller": {
            "name": settings.SELLER_NAME,
            "inn": settings.SELLER_INN,
            "phone": settings.SELLER_PHONE,
            "phone_uri": f"+{phone_digits}" if phone_digits else "",
            "email": settings.SELLER_EMAIL,
            "city": settings.SELLER_CITY,
            "address": settings.SELLER_ADDRESS,
        },
        "delivery": {
            "price": settings.DELIVERY_PRICE,
            "time": settings.DELIVERY_TIME,
        },
    }
