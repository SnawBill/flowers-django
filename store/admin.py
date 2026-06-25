from django.contrib import admin

from .models import CartItem, Product, ProductImage, Tag


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image_url", "sort_order")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "is_active")
    list_editable = ("price", "is_active")
    search_fields = ("title", "tags__name")
    filter_horizontal = ("tags",)
    inlines = [ProductImageInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "quantity")
    search_fields = ("user__username", "product__title")
