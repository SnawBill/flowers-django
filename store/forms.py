from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Order, Product, Profile


# Форма регистрации с обязательным email.
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Почта")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": "Имя",
            "password1": "Пароль",
            "password2": "Подтвердите пароль",
        }

    # Сохраняем email в стандартную модель пользователя Django.
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


# Форма создания и редактирования товара для администратора.
class ProductForm(forms.ModelForm):
    tags_text = forms.CharField(
        label="Теги",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "розовый, букет, свадьба"}),
    )
    gallery_text = forms.CharField(
        label="Галерея",
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "Один URL на строку"}),
    )

    class Meta:
        model = Product
        fields = ("title", "price", "description", "image_url", "is_active")
        labels = {
            "title": "Название",
            "price": "Цена",
            "description": "Описание",
            "image_url": "URL изображения",
            "is_active": "Наличие",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Короткое описание букета"}),
            "image_url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    # При редактировании заполняем теги и галерею в текстовые поля.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["tags_text"].initial = ", ".join(self.instance.tags.values_list("name", flat=True))
            self.fields["gallery_text"].initial = "\n".join(
                self.instance.gallery_images.order_by("sort_order").values_list("image_url", flat=True)
            )


# Необязательные данные профиля, которые упрощают повторное оформление заказа.
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "phone", "address")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "phone": "Номер телефона",
            "address": "Адрес",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Имя"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Фамилия"}),
            "phone": forms.TextInput(attrs={"placeholder": "+7..."}),
            "address": forms.Textarea(attrs={"rows": 4, "placeholder": "Адрес доставки"}),
        }


# Финальная форма оформления заказа перед оплатой.
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("full_name", "phone", "address", "email", "payment_method", "comment")
        labels = {
            "full_name": "Имя получателя",
            "phone": "Телефон",
            "address": "Адрес доставки",
            "email": "Email",
            "payment_method": "Способ оплаты",
            "comment": "Комментарий к заказу",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Например, Владислав Иванов"}),
            "phone": forms.TextInput(attrs={"placeholder": "+7 (999) 123-45-67"}),
            "address": forms.Textarea(attrs={"rows": 4, "placeholder": "Город, улица, дом, квартира"}),
            "email": forms.EmailInput(attrs={"placeholder": "example@mail.ru"}),
            "payment_method": forms.Select(),
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Пожелания к доставке или открытке"}),
        }
