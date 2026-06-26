# Flowers Django

Django-магазин букетов с PostgreSQL.

## Запуск

```bash
git clone https://github.com/SnawBill/flowers-django.git
cd flowers-django
uv sync
cp .env.example .env
```

Создай базу PostgreSQL:

```bash
sudo -u postgres psql
```

```sql
CREATE USER "user" WITH PASSWORD 'password';
CREATE DATABASE flower_shop OWNER "user";
GRANT ALL PRIVILEGES ON DATABASE flower_shop TO "user";
\q
```

Примени миграции и загрузи товары из базы:

```bash
uv run python manage.py migrate
uv run python manage.py loaddata store/fixtures/catalog_data.json
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Что передается вместе с проектом

- код проекта
- структура базы через миграции
- товары, теги и галерея в файле [catalog_data.json](/home/vlad/flowers_django/store/fixtures/catalog_data.json)

## Адреса

- сайт: `http://127.0.0.1:8000`
- админка: `http://127.0.0.1:8000/admin/`
- заказы: `http://127.0.0.1:8000/admin/orders/`
