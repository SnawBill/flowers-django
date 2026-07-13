from django.urls import path

from . import views


# Публичные маршруты магазина, корзины, профиля и каталога.
urlpatterns = [
    path("", views.index, name="index"),
    path("contacts/", views.contacts_view, name="contacts"),
    path("delivery/", views.delivery_view, name="delivery"),
    path("offer/", views.offer_view, name="offer"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("requisites/", views.requisites_view, name="requisites"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("orders/<int:order_id>/pay/", views.start_payment_view, name="start_payment"),
    path("payments/yookassa/simulate/<int:order_id>/", views.yookassa_simulator_view, name="yookassa_simulator"),
    path("payments/yookassa/return/", views.yookassa_return_view, name="yookassa_return"),
    path("payments/yookassa/webhook/", views.yookassa_webhook_view, name="yookassa_webhook"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/<int:item_id>/increase/", views.increase_cart_item, name="increase_cart_item"),
    path("cart/<int:item_id>/decrease/", views.decrease_cart_item, name="decrease_cart_item"),
    path("remove-from-cart/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("products/create/", views.create_product, name="create_product"),
    path("products/<int:product_id>/edit/", views.edit_product, name="edit_product"),
    path("products/<int:product_id>/delete/", views.delete_product, name="delete_product"),
]
