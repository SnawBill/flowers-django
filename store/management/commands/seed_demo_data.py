from django.core.management.base import BaseCommand

from store.demo_data import PRODUCTS
from store.models import CartItem, Product, ProductImage, Tag


class Command(BaseCommand):
    help = "Replace the catalog with demo flower products"

    def handle(self, *args, **options):
        CartItem.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Tag.objects.all().delete()

        created = 0
        for item in PRODUCTS:
            product = Product.objects.create(
                title=item["title"],
                price=item["price"],
                image_url=item["image_url"],
                description=item.get("description", ""),
                is_active=True,
            )
            tags = []
            for tag_name in item.get("tags", []):
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            product.tags.set(tags)
            for order, image_url in enumerate(item.get("gallery_images", []), start=1):
                ProductImage.objects.create(product=product, image_url=image_url, sort_order=order)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Replaced catalog with {created} products."))
