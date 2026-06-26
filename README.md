# Flowers Django

## Запуск

```bash
git clone https://github.com/SnawBill/flowers-django.git
cd flowers-django
uv sync
cp .env.example .env
```

Создай пользователя и базу PostgreSQL:

```bash
sudo -u postgres psql
```

```sql
CREATE USER "user" WITH PASSWORD 'password';
CREATE DATABASE flower_shop OWNER "user";
GRANT ALL PRIVILEGES ON DATABASE flower_shop TO "user";
\q
```

Восстанови базу из дампа:

```bash
psql -h 127.0.0.1 -U user -d flower_shop < flowers_django_dump.sql
```

Запусти проект:

```bash
uv run python manage.py runserver
```

## Адреса

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/admin/orders/`
