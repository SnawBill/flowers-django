# Flowers Django

Интернет-магазин цветочных букетов на Django с каталогом товаров, корзиной, оформлением заказа, профилем пользователя и административным управлением товарами и заказами.

## Скриншоты

После добавления изображений в `docs/screenshots/` они будут отображаться здесь.

Рекомендуемые имена файлов:

- `home.png` — главная страница
- `product.png` — страница товара
- `cart.png` — корзина или оформление заказа
- `admin-orders.png` — страница заказов администратора

Markdown для вставки изображений:

```md
![Главная страница](docs/screenshots/home.png)
![Страница товара](docs/screenshots/product.png)
![Корзина](docs/screenshots/cart.png)
![Заказы администратора](docs/screenshots/admin-orders.png)
```

Если положишь файлы именно с этими именами, просто замени этот блок на:

```md
![Главная страница](docs/screenshots/home.png)
![Страница товара](docs/screenshots/product.png)
![Корзина](docs/screenshots/cart.png)
![Заказы администратора](docs/screenshots/admin-orders.png)
```

## Возможности

- регистрация, вход и выход пользователей
- профиль пользователя с редактированием контактных данных
- каталог букетов с фильтрацией по цене и тегам
- страница товара с галереей и похожими товарами
- корзина с изменением количества товаров
- оформление заказа
- тестовая интеграция оплаты через ЮKassa
- история и управление заказами для администратора
- создание, редактирование и удаление товаров администратором

## Стек

- Python 3.10+
- Django
- PostgreSQL
- UV
- HTML / CSS / JavaScript

## Запуск проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/SnawBill/flowers-django.git
cd flowers-django
```

### 2. Установка зависимостей

```bash
uv sync
```

### 3. Настройка переменных окружения

Создай файл `.env` на основе `.env.example`.

Пример переменных:

```env
SECRET_KEY=your-secret-key
DEBUG=1
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgresql://postgres:password@localhost:5432/flowers_django
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
YOOKASSA_SIMULATION=1
PAYMENT_BASE_URL=http://127.0.0.1:8000
```

Если `DATABASE_URL` не задан, проект использует локальную SQLite базу как fallback.

### 4. Применение миграций

```bash
uv run python manage.py migrate
```

### 5. Создание суперпользователя

```bash
uv run python manage.py createsuperuser
```

### 6. Запуск сервера

```bash
uv run python manage.py runserver
```

Открыть в браузере:

- сайт: `http://127.0.0.1:8000`
- админка Django: `http://127.0.0.1:8000/admin/`
- заказы администратора: `http://127.0.0.1:8000/admin/orders/`

## Структура проекта

```text
flowers_django/
├── docs/screenshots/  # скриншоты для README
├── flowers_django/    # настройки проекта, маршруты, ASGI/WSGI
├── store/             # логика магазина: модели, views, формы, сигналы
├── static/            # стили, иконки, скрипты
├── templates/         # HTML-шаблоны
├── manage.py
├── pyproject.toml
└── README.md
```

## Основные сущности

- `Product` — товар каталога
- `ProductImage` — изображения галереи товара
- `Tag` — теги для фильтрации и похожих товаров
- `Profile` — данные пользователя для доставки
- `CartItem` — позиция в корзине
- `Order` — заказ
- `OrderItem` — снимок товара в составе заказа

## Оплата

В проекте реализована тестовая логика оплаты через ЮKassa.

Режим симуляции включается так:

```env
YOOKASSA_SIMULATION=1
```

В этом режиме можно проверить пользовательский сценарий оплаты без реального эквайринга.

## Git

Базовый цикл работы:

```bash
git add .
git commit -m "Описание изменений"
git push
```

## Автор

Проект оформлен как учебный интернет-магазин цветочной продукции.
