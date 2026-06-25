from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .demo_data import DEMO_PRODUCTS
from .models import CartItem, Product, ProductImage, Tag


# После миграций один раз наполняем каталог демонстрационными товарами.
@receiver(post_migrate)
def seed_demo_products(sender, **kwargs):
    if sender.name != "store":
        return

    for item in DEMO_PRODUCTS:
        matching_products = list(Product.objects.filter(title=item["title"]).order_by("id"))
        if matching_products:
            product = matching_products[0]
            # Если вдруг появились дубликаты, оставляем только первый товар.
            for duplicate in matching_products[1:]:
                CartItem.objects.filter(product=duplicate).delete()
                duplicate.delete()
        else:
            product = Product.objects.create(
                title=item["title"],
                price=item["price"],
                image_url=item["image_url"],
                is_active=True,
            )

        # Теги и галерея заполняются только для еще пустых записей,
        # чтобы не перетирать ручные правки администратора.
        if not product.tags.exists():
            tags = []
            for tag_name in item.get("tags", []):
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            product.tags.set(tags)

        if not product.gallery_images.exists():
            for order, image_url in enumerate(item.get("gallery_images", []), start=1):
                ProductImage.objects.get_or_create(
                    product=product,
                    image_url=image_url,
                    defaults={"sort_order": order},
                )
