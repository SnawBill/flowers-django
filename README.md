# Flowers Django

## Запуск на сервере

Нужны Docker и Docker Compose.

```bash
git clone https://github.com/SnawBill/flowers-django.git
cd flowers-django
cp .env.example .env
```

В `.env` замени `SECRET_KEY`, пароль PostgreSQL, домен в `ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS` и `PAYMENT_BASE_URL`. Пароль в `POSTGRES_PASSWORD`
должен совпадать с паролем внутри `DATABASE_URL`.

Для симуляции оплаты оставь `YOOKASSA_SIMULATION=1`. Для реальных платежей
укажи ключи ЮKassa и установи `YOOKASSA_SIMULATION=0`.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Сайт откроется по IP-адресу сервера. При первом запуске PostgreSQL автоматически
восстановит товары и остальные данные из `flowers_django_dump.sql`.

Создание нового администратора:

```bash
docker compose -f docker-compose.prod.yml exec web .venv/bin/python manage.py createsuperuser
```

Логи:

```bash
docker compose -f docker-compose.prod.yml logs -f
```

Повторное восстановление дампа требует удаления существующего тома PostgreSQL и
удалит текущие данные:

```bash
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up --build -d
```

После настройки HTTPS у хостинг-провайдера или во внешнем reverse proxy укажи в `.env`:

```env
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
SECURE_HSTS_SECONDS=31536000
```
