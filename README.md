# Flowers Django

## Запуск на сервере

Нужны Docker и Docker Compose.

```bash
git clone https://github.com/SnawBill/flowers-django.git
cd flowers-django
cp .env.example .env
```

В `.env` замени `SECRET_KEY`, пароль PostgreSQL и `example.com` на свой домен.
Пароль в `POSTGRES_PASSWORD` должен совпадать с паролем внутри `DATABASE_URL`.
DNS-записи домена должны указывать на IP сервера, а порты `80` и `443` должны
быть открыты.

Для симуляции оплаты оставь `YOOKASSA_SIMULATION=1`. Для реальных платежей
укажи `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY` и установи
`YOOKASSA_SIMULATION=0`. Для тестового магазина оставь
`YOOKASSA_TEST_MODE=1`, для настоящего установи `YOOKASSA_TEST_MODE=0`.
В личном кабинете ЮKassa добавь URL уведомлений:
`https://example.com/payments/yookassa/webhook/` для событий
`payment.succeeded` и `payment.canceled`.

Если в магазине подключены чеки от ЮKassa, установи
`YOOKASSA_RECEIPTS_ENABLED=1` и укажи подходящий код НДС в
`YOOKASSA_VAT_CODE`. Код должен соответствовать настройкам кассы и системе
налогообложения.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Сайт откроется по HTTPS на домене из `DOMAIN`. Caddy автоматически выпустит и
будет продлевать TLS-сертификат. При первом запуске PostgreSQL автоматически
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
