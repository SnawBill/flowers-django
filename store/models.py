from django.conf import settings
from django.db import models


# Справочник тегов для фильтрации и подбора похожих букетов.
class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# Основная карточка товара, которая показывается в каталоге и деталке.
class Product(models.Model):
    title = models.CharField(max_length=120)
    price = models.PositiveIntegerField()
    description = models.TextField(blank=True, default="")
    image_url = models.URLField()
    is_active = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


# Дополнительные изображения для галереи конкретного букета.
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery_images")
    image_url = models.URLField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.title} #{self.sort_order}"


# Расширение стандартного пользователя с данными для доставки.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


# Текущая корзина пользователя: одна строка на товар.
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [["user", "product"]]

    def __str__(self):
        return f"{self.user} / {self.product}"


# Заказ хранит контактные данные, статус оплаты и итоговую сумму.
class Order(models.Model):
    PAYMENT_METHOD_CARD = "card"
    PAYMENT_METHOD_SBP = "sbp"
    PAYMENT_METHOD_CASH = "cash"
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CARD, "Банковская карта"),
        (PAYMENT_METHOD_SBP, "СБП"),
        (PAYMENT_METHOD_CASH, "Курьеру при получении"),
    ]

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELED = "canceled"
    STATUS_FAILED = "failed"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает оплаты"),
        (STATUS_PAID, "Оплачен"),
        (STATUS_COMPLETED, "Завершен"),
        (STATUS_CANCELED, "Отменен"),
        (STATUS_FAILED, "Ошибка оплаты"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    comment = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    provider_payment_id = models.CharField(max_length=120, blank=True, default="")
    paid_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Заказ #{self.pk} - {self.full_name}"


# Снимок товара в заказе, чтобы состав не менялся после редактирования каталога.
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_title = models.CharField(max_length=120)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.product_title} x{self.quantity}"
