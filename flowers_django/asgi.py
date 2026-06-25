import os

from django.core.asgi import get_asgi_application

# Настройка ASGI-приложения для асинхронных серверов.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowers_django.settings")

application = get_asgi_application()
