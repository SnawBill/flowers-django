import json
import logging
import re
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import CheckoutForm, ProductForm, ProfileForm, RegistrationForm
from .models import CartItem, Order, OrderItem, Product, ProductImage, Profile, Tag
from .payments import YooKassaError, create_payment, fetch_payment, validate_payment, yookassa_enabled


logger = logging.getLogger(__name__)


# Единая проверка прав администратора для шаблонов и views.
def _is_admin(user):
    return user.is_authenticated and user.is_staff


# Разбираем строки тегов и URL-ов галереи из textarea/inputs администратора.
def _split_values(raw_text):
    seen = set()
    values = []
    for chunk in re.split(r"\n|,", raw_text or ""):
        value = chunk.strip()
        if value and value not in seen:
            seen.add(value)
            values.append(value)
    return values


# Синхронизируем связи товара после сохранения основной формы.
def _sync_product_relations(product, tags_text, gallery_text):
    tags = []
    for tag_name in _split_values(tags_text):
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)
    product.tags.set(tags)

    product.gallery_images.all().delete()
    for order, image_url in enumerate(_split_values(gallery_text), start=1):
        ProductImage.objects.create(product=product, image_url=image_url, sort_order=order)


# Базовый адрес нужен ЮKassa для return_url и локальной симуляции.
def _payment_base_url(request):
    if settings.PAYMENT_BASE_URL:
        return settings.PAYMENT_BASE_URL.rstrip("/")
    return request.build_absolute_uri("/").rstrip("/")


# Собираем абсолютный URL по имени маршрута.
def _build_absolute_url(request, route_name, **kwargs):
    return f"{_payment_base_url(request)}{reverse(route_name, kwargs=kwargs)}"


# Помечаем заказ как оплаченный и очищаем корзину пользователя.
def _mark_order_paid(order):
    if order.status in {Order.STATUS_PAID, Order.STATUS_COMPLETED}:
        return
    order.status = Order.STATUS_PAID
    order.paid_at = timezone.now()
    order.save(update_fields=["status", "paid_at"])
    CartItem.objects.filter(user=order.user).delete()


# Универсально меняем статус заказа без дублирования логики по датам.
def _mark_order_status(order, status):
    fields = ["status"]
    order.status = status
    if status == Order.STATUS_PAID and not order.paid_at:
        order.paid_at = timezone.now()
        fields.append("paid_at")
    if status != Order.STATUS_COMPLETED and order.completed_at is not None:
        order.completed_at = None
        fields.append("completed_at")
    order.save(update_fields=fields)


# Завершенный заказ считается выданным клиенту.
def _mark_order_completed(order):
    fields = []
    if order.status != Order.STATUS_PAID and order.paid_at is None:
        order.paid_at = timezone.now()
        fields.append("paid_at")
    order.status = Order.STATUS_COMPLETED
    order.completed_at = timezone.now()
    fields.extend(["status", "completed_at"])
    order.save(update_fields=list(dict.fromkeys(fields)))
    CartItem.objects.filter(user=order.user).delete()


# Завершенные более недели назад заказы скрываем из админского списка.
def _visible_orders_queryset():
    expires_before = timezone.now() - timedelta(days=7)
    return Order.objects.exclude(
        status=Order.STATUS_COMPLETED,
        completed_at__isnull=False,
        completed_at__lt=expires_before,
    )


def _apply_yookassa_status(order, payment):
    validate_payment(order, payment)
    status = payment.get("status")
    if status == "succeeded":
        _mark_order_paid(order)
    elif status == "canceled" and order.status not in {Order.STATUS_PAID, Order.STATUS_COMPLETED}:
        _mark_order_status(order, Order.STATUS_CANCELED)
    return status


# Главная страница с каталогом и фильтрами по тегам и цене.
def index(request):
    products = Product.objects.filter(is_active=True).prefetch_related("tags")
    available_tags = Tag.objects.order_by("name")
    selected_tags = request.GET.getlist("tag")
    min_price = (request.GET.get("min_price") or "").strip()
    max_price = (request.GET.get("max_price") or "").strip()

    if min_price:
        try:
            products = products.filter(price__gte=int(min_price))
        except ValueError:
            min_price = ""

    if max_price:
        try:
            products = products.filter(price__lte=int(max_price))
        except ValueError:
            max_price = ""

    if selected_tags:
        products = products.filter(tags__name__in=selected_tags).distinct()

    context = {
        "products": products,
        "user_is_admin": _is_admin(request.user),
        "available_tags": available_tags,
        "selected_tags": selected_tags,
        "min_price": min_price,
        "max_price": max_price,
        "tag_filter_applied": bool(selected_tags),
    }
    return render(request, "store/index.html", context)


def contacts_view(request):
    return render(request, "store/contacts.html")


def delivery_view(request):
    return render(request, "store/delivery.html")


def offer_view(request):
    return render(request, "store/offer.html")


def privacy_view(request):
    return render(request, "store/privacy.html")


def requisites_view(request):
    return render(request, "store/requisites.html")


# Детальная страница товара с галереей и похожими позициями по совпадающим тегам.
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    product_tags = list(product.tags.all())
    related_products = Product.objects.filter(is_active=True).exclude(pk=product.pk)
    if product_tags:
        related_products = (
            related_products.filter(tags__in=product_tags)
            .annotate(shared_tags=Count("tags", filter=Q(tags__in=product_tags), distinct=True))
            .order_by("-shared_tags", "id")
            .distinct()
        )
    related_products = list(related_products[:3])

    # Основное фото тоже попадает в галерею, затем убираем дубликаты URL.
    gallery_images = [product.image_url]
    gallery_images.extend(product.gallery_images.values_list("image_url", flat=True))
    deduped_gallery = []
    seen = set()
    for image_url in gallery_images:
        if image_url not in seen:
            seen.add(image_url)
            deduped_gallery.append(image_url)

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "product_tags": product_tags,
            "related_products": related_products,
            "gallery_images": deduped_gallery,
            "user_is_admin": _is_admin(request.user),
        },
    )


# Регистрация сразу авторизует пользователя и создает профиль.
def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        Profile.objects.get_or_create(user=user)
        messages.success(request, "Вы успешно зарегистрированы.")
        return redirect("index")
    return render(request, "store/register.html", {"form": form})


# Стандартный вход через форму аутентификации Django.
def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        Profile.objects.get_or_create(user=request.user)
        return redirect("index")
    return render(request, "store/login.html", {"form": form})


# Выход просто очищает сессию и возвращает на главную.
def logout_view(request):
    logout(request)
    return redirect("index")


# Просмотр профиля пользователя.
@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "store/profile.html", {"user_profile": request.user, "profile": profile})


# Редактирование дополнительных данных профиля.
@login_required
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Профиль обновлен.")
        return redirect("profile")
    return render(request, "store/profile_edit.html", {"form": form, "profile": profile})


# Добавление товара в корзину. Для администратора действие запрещено.
@login_required
def add_to_cart(request, product_id):
    if _is_admin(request.user):
        messages.warning(request, "Администратор не может добавлять товары в корзину.")
        return redirect("index")

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        CartItem.objects.filter(pk=item.pk).update(quantity=F("quantity") + 1)
    messages.success(request, f"Добавлено: {product.title}")
    return redirect("index")


# Корзина с подсчетом общей суммы.
@login_required
def cart_view(request):
    cart_items = CartItem.objects.select_related("product").filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, "store/cart.html", {"cart_items": cart_items, "total_price": total_price})


# Оформление заказа создает Order и копирует в него товары из корзины.
@login_required
def checkout_view(request):
    if _is_admin(request.user):
        messages.warning(request, "Администратор не оформляет заказы через корзину.")
        return redirect("index")

    cart_items = list(CartItem.objects.select_related("product").filter(user=request.user))
    if not cart_items:
        messages.warning(request, "Ваша корзина пуста.")
        return redirect("cart")

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    initial = {
        "full_name": " ".join(filter(None, [profile.first_name, profile.last_name])).strip() or request.user.username,
        "phone": profile.phone,
        "address": profile.address,
        "email": request.user.email,
    }
    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        order = form.save(commit=False)
        order.user = request.user
        order.total_price = total_price
        order.status = order.STATUS_PENDING
        order.save()

        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product_title=item.product.title,
                    price=item.product.price,
                    quantity=item.quantity,
                    image_url=item.product.image_url,
                )
                for item in cart_items
            ]
        )

        # Профиль обновляем из последней удачной формы оформления.
        profile.phone = form.cleaned_data["phone"]
        profile.address = form.cleaned_data["address"]
        full_name = form.cleaned_data["full_name"].strip().split(maxsplit=1)
        profile.first_name = full_name[0] if full_name else profile.first_name
        profile.last_name = full_name[1] if len(full_name) > 1 else profile.last_name
        profile.save()

        return redirect("start_payment", order_id=order.id)

    return render(
        request,
        "store/checkout.html",
        {
            "form": form,
            "cart_items": cart_items,
            "total_price": total_price,
            "yookassa_simulation": settings.YOOKASSA_SIMULATION or not yookassa_enabled(),
        },
    )


# Запуск оплаты: либо реальный редирект в ЮKassa, либо локальный симулятор.
@login_required
def start_payment_view(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=order_id, user=request.user)
    if order.status in {Order.STATUS_PAID, Order.STATUS_COMPLETED}:
        messages.success(request, f"Заказ №{order.id} уже оплачен.")
        return redirect("index")

    if order.payment_method == Order.PAYMENT_METHOD_CASH:
        CartItem.objects.filter(user=order.user).delete()
        messages.success(request, f"Заказ №{order.id} оформлен. Оплата производится курьеру при получении.")
        return redirect("index")

    if order.status in {Order.STATUS_CANCELED, Order.STATUS_FAILED}:
        messages.warning(request, "Этот платеж завершен. Оформите новый заказ из текущей корзины.")
        return redirect("cart")

    if settings.YOOKASSA_SIMULATION or not yookassa_enabled():
        return redirect("yookassa_simulator", order_id=order.id)

    try:
        if order.provider_payment_id:
            payment = validate_payment(order, fetch_payment(order.provider_payment_id))
        else:
            return_url = _build_absolute_url(request, "yookassa_return") + f"?order_id={order.id}"
            payment = validate_payment(order, create_payment(order, return_url))
            order.provider_payment_id = payment["id"]
            order.save(update_fields=["provider_payment_id"])
    except YooKassaError:
        logger.exception("Не удалось создать или получить платеж ЮKassa для заказа %s", order.id)
        messages.error(request, "ЮKassa временно недоступна. Попробуйте перейти к оплате еще раз.")
        return redirect("cart")

    status = _apply_yookassa_status(order, payment)
    if status == "succeeded":
        messages.success(request, f"Оплата заказа №{order.id} уже подтверждена.")
        return redirect("index")
    if status == "canceled":
        messages.warning(request, "Платеж отменен. Оформите новый заказ.")
        return redirect("cart")
    confirmation = payment.get("confirmation", {})
    confirmation_url = confirmation.get("confirmation_url")
    if not confirmation_url:
        messages.error(request, "ЮKassa не вернула ссылку на оплату.")
        return redirect("checkout")
    return redirect(confirmation_url)


# Локальная страница-симулятор для тестовой оплаты без реального эквайринга.
@login_required
def yookassa_simulator_view(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=order_id, user=request.user)
    if order.status == Order.STATUS_PAID:
        messages.success(request, f"Заказ №{order.id} уже оплачен.")
        return redirect("index")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "success":
            _mark_order_paid(order)
            messages.success(request, f"Тестовая оплата ЮKassa прошла успешно. Заказ №{order.id} оплачен.")
            return redirect("index")
        if action == "cancel":
            _mark_order_status(order, Order.STATUS_CANCELED)
            messages.warning(request, f"Тестовая оплата ЮKassa отменена для заказа №{order.id}.")
            return redirect("cart")
        _mark_order_status(order, Order.STATUS_FAILED)
        messages.error(request, f"Во время тестовой оплаты ЮKassa произошла ошибка для заказа №{order.id}.")
        return redirect("cart")

    return render(request, "store/yookassa_simulator.html", {"order": order})


# Обработка возврата пользователя после оплаты в ЮKassa.
@login_required
def yookassa_return_view(request):
    order_id = request.GET.get("order_id")
    if not order_id:
        messages.warning(request, "Не удалось определить заказ после возврата из ЮKassa.")
        return redirect("index")

    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.status in {Order.STATUS_PAID, Order.STATUS_COMPLETED}:
        messages.success(request, f"Оплата подтверждена. Заказ №{order.id} уже оплачен.")
        return redirect("index")

    if order.provider_payment_id and yookassa_enabled():
        try:
            payment = fetch_payment(order.provider_payment_id)
            status = _apply_yookassa_status(order, payment)
        except YooKassaError:
            logger.exception("Не удалось проверить платеж ЮKassa для заказа %s", order.id)
            messages.warning(request, "ЮKassa еще не подтвердила платеж. Проверьте статус позже.")
            return redirect("cart")

        if status == "succeeded":
            messages.success(request, f"Оплата ЮKassa подтверждена. Заказ №{order.id} оплачен.")
            return redirect("index")
        if status == "canceled":
            messages.warning(request, f"ЮKassa сообщила об отмене платежа по заказу №{order.id}.")
            return redirect("cart")

    messages.info(request, "Платеж создан и ожидает подтверждения ЮKassa.")
    return redirect("cart")


# Вебхук для фонового обновления статусов, если ЮKassa уведомила сервер раньше пользователя.
@csrf_exempt
def yookassa_webhook_view(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"ok": False, "error": "invalid_payload"}, status=400)

    payment_object = payload.get("object", {})
    if not isinstance(payment_object, dict):
        return JsonResponse({"ok": False, "error": "invalid_payload"}, status=400)
    payment_id = payment_object.get("id")
    if not payment_id:
        return JsonResponse({"ok": True})
    if not yookassa_enabled():
        return JsonResponse({"ok": False}, status=503)

    order = Order.objects.filter(provider_payment_id=payment_id).first()
    if not order:
        order_id = (payment_object.get("metadata") or {}).get("order_id")
        order = Order.objects.filter(pk=order_id).first() if order_id else None
    if not order:
        return JsonResponse({"ok": True})

    try:
        payment = fetch_payment(payment_id)
        validate_payment(order, payment)
    except YooKassaError:
        logger.exception("Не удалось проверить webhook ЮKassa для платежа %s", payment_id)
        return JsonResponse({"ok": False}, status=503)

    if not order.provider_payment_id:
        order.provider_payment_id = payment_id
        order.save(update_fields=["provider_payment_id"])
    _apply_yookassa_status(order, payment)

    return JsonResponse({"ok": True})


# Увеличение количества товара в корзине.
@login_required
def increase_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    if item.user_id != request.user.id:
        messages.error(request, "Недостаточно прав.")
        return redirect("cart")

    CartItem.objects.filter(pk=item.pk).update(quantity=F("quantity") + 1)
    messages.success(request, f"Количество товара увеличено: {item.product.title}")
    return redirect("cart")


# Уменьшение количества, а при единице - удаление строки корзины.
@login_required
def decrease_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    if item.user_id != request.user.id:
        messages.error(request, "Недостаточно прав.")
        return redirect("cart")

    if item.quantity <= 1:
        item.delete()
        messages.success(request, f"Товар удален из корзины: {item.product.title}")
    else:
        CartItem.objects.filter(pk=item.pk).update(quantity=F("quantity") - 1)
        messages.success(request, f"Количество товара уменьшено: {item.product.title}")
    return redirect("cart")


# Полное удаление товара из корзины.
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    if item.user_id != request.user.id:
        messages.error(request, "Недостаточно прав.")
        return redirect("cart")
    item.delete()
    return redirect("cart")


# Список заказов для администратора.
@login_required
def admin_orders_view(request):
    if not _is_admin(request.user):
        messages.error(request, "Недостаточно прав для просмотра заказов.")
        return redirect("index")

    orders = _visible_orders_queryset().select_related("user").prefetch_related("items").order_by("-created_at", "-id")
    return render(request, "store/admin_orders.html", {"orders": orders})


# Карточка отдельного заказа с возможностью смены статуса.
@login_required
def admin_order_detail_view(request, order_id):
    if not _is_admin(request.user):
        messages.error(request, "Недостаточно прав для просмотра заказа.")
        return redirect("index")

    order = get_object_or_404(_visible_orders_queryset().select_related("user").prefetch_related("items"), pk=order_id)
    status_choices = Order.STATUS_CHOICES

    if request.method == "POST":
        action = request.POST.get("action", "update_status")
        if action == "complete_order":
            _mark_order_completed(order)
            messages.success(request, f"Заказ №{order.id} завершен. Клиент получил товар.")
            return redirect("admin_order_detail", order_id=order.id)

        new_status = request.POST.get("status", "")
        valid_statuses = {choice[0] for choice in status_choices}
        if new_status not in valid_statuses:
            messages.error(request, "Выбран некорректный статус заказа.")
            return redirect("admin_order_detail", order_id=order.id)

        if new_status == Order.STATUS_COMPLETED:
            _mark_order_completed(order)
        elif new_status == Order.STATUS_PAID:
            _mark_order_paid(order)
        else:
            _mark_order_status(order, new_status)
        messages.success(request, f"Статус заказа №{order.id} обновлен.")
        return redirect("admin_order_detail", order_id=order.id)

    return render(
        request,
        "store/admin_order_detail.html",
        {
            "order": order,
            "status_choices": status_choices,
        },
    )


# Создание товара администратором.
@login_required
def create_product(request):
    if not _is_admin(request.user):
        messages.error(request, "Недостаточно прав для добавления товара.")
        return redirect("index")

    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        _sync_product_relations(product, form.cleaned_data.get("tags_text"), form.cleaned_data.get("gallery_text"))
        messages.success(request, "Товар добавлен.")
        return redirect("index")
    return render(request, "store/create_product.html", {"form": form})


# Редактирование существующего товара администратором.
@login_required
def edit_product(request, product_id):
    if not _is_admin(request.user):
        messages.error(request, "Недостаточно прав для редактирования товара.")
        return redirect("index")

    product = get_object_or_404(Product, pk=product_id)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        _sync_product_relations(product, form.cleaned_data.get("tags_text"), form.cleaned_data.get("gallery_text"))
        messages.success(request, "Товар обновлен.")
        return redirect("index")
    return render(request, "store/edit_product.html", {"form": form, "product": product})


# Удаление товара с очисткой связанных позиций в корзинах.
@login_required
def delete_product(request, product_id):
    if not _is_admin(request.user):
        messages.error(request, "Недостаточно прав для удаления товара.")
        return redirect("index")

    product = get_object_or_404(Product, pk=product_id)
    CartItem.objects.filter(product=product).delete()
    product.delete()
    messages.success(request, "Товар удален.")
    return redirect("index")
