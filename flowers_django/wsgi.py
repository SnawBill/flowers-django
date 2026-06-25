import os

from django.core.wsgi import get_wsgi_application

# Настройка WSGI-приложения для обычного деплоя.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowers_django.settings")

application = get_wsgi_application()
