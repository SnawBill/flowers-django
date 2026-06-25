from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "store"

    # Подключаем сигналы после инициализации приложения.
    def ready(self):
        from . import signals  # noqa: F401
