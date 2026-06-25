from django.contrib import admin
from django.urls import include, path

from store import views as store_views


# Часть админских страниц вынесена в пользовательские views,
# поэтому маршруты для заказов объявлены до стандартной Django-админки.
urlpatterns = [
    path("admin/orders/", store_views.admin_orders_view, name="admin_orders"),
    path("admin/orders/<int:order_id>/", store_views.admin_order_detail_view, name="admin_order_detail"),
    path("admin/", admin.site.urls),
    path("", include("store.urls")),
]
