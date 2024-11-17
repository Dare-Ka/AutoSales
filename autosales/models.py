from typing import Any, Optional

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator

STATE_CHOICES = (
    ("basket", "Статус корзины"),
    ("new", "Новый"),
    ("confirmed", "Подтвержден"),
    ("assembled", "Собран"),
    ("sent", "Отправлен"),
    ("delivered", "Доставлен"),
    ("canceled", "Отменен"),
)

USER_TYPE_CHOICES = (
    ("shop", "Магазин"),
    ("buyer", "Покупатель"),
)


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Optional[dict]
    ) -> "User":
        if not email:
            raise ValueError(_("Users must have an email address"))
        extra_fields.setdefault("is_stuff", False)
        extra_fields.setdefault("is_superuser", False)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str, **extra_fields: Optional[dict]
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()
    USERNAME_FIELD = "email"
    email = models.EmailField(verbose_name=_("Email address"), unique=True)
    company = models.CharField(verbose_name=_("Company"), max_length=40, blank=True)
    position = models.CharField(verbose_name=_("Position"), max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        verbose_name=_("Username"),
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        max_length=150,
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    type = models.CharField(
        verbose_name=_("User type"),
        choices=USER_TYPE_CHOICES,
        max_length=5,
        default="buyer",
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} "

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"
        ordering = ("email",)


class Shop(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=50)
    url = models.URLField(verbose_name=_("Link"), null=True, blank=True)
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="shops",
        blank=True,
        null=True,
    )
    state = models.BooleanField(verbose_name=_("Order receipt status"), default=True)

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"
        ordering = ("-name",)

    def __str__(self) -> str:
        return f"{self.name}: {self.url}"


class Contact(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        related_name="contacts",
        blank=True,
        on_delete=models.CASCADE,
    )
    city = models.CharField(max_length=50, verbose_name=_("City"))
    street = models.CharField(max_length=100, verbose_name=_("Street"))
    house = models.CharField(max_length=15, verbose_name=_("House"), blank=True)
    structure = models.CharField(max_length=15, verbose_name=_("Structure"), blank=True)
    building = models.CharField(max_length=15, verbose_name=_("Building"), blank=True)
    apartment = models.CharField(max_length=15, verbose_name=_("Apartment"), blank=True)
    phone = models.CharField(max_length=20, verbose_name=_("Phone number"))

    class Meta:
        verbose_name = "Контакты пользователя"
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self) -> str:
        return f"{self.user}:{self.city} {self.street} {self.house}"


class Category(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=40)
    shops = models.ManyToManyField(
        Shop, verbose_name=_("Shops"), related_name="categories", blank=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Список категорий"
        ordering = ("-name",)

    def __str__(self) -> str:
        return f"{self.name}: {self.shops}"


class Product(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=80)
    categories = models.ManyToManyField(
        Category,
        verbose_name=_("Categories)"),
        related_name="categories",
        blank=True,
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Список продуктов"
        ordering = ("-name",)

    def __str__(self) -> str:
        return f"{self.name}: {self.categories}"


class ProductInfo(models.Model):
    model = models.CharField(verbose_name=_("Model"), max_length=80, blank=True)
    external_id = models.PositiveIntegerField(verbose_name=_("External ID"))
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        related_name="product_infos",
        blank=True,
        on_delete=models.CASCADE,
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name=_("Shop"),
        related_name="product_infos",
        blank=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))
    price = models.PositiveIntegerField(verbose_name=_("Price"))
    price_rrc = models.PositiveIntegerField(verbose_name=_("Recommended retail price"))

    class Meta:
        verbose_name = "Информация о продукте"
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "shop", "external_id"], name="unique_product_info"
            ),
        ]

    def __str__(self) -> str:
        return self.model


class Parameter(models.Model):
    name = models.CharField(max_length=40, verbose_name=_("Name"))

    class Meta:
        verbose_name = "Имя параметра"
        verbose_name_plural = "Список имен параметров"
        ordering = ("-name",)

    def __str__(self) -> str:
        return str(self.name)


class ProductParameter(models.Model):
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name=_("Product`s information"),
        related_name="product_parameters",
        blank=True,
        on_delete=models.CASCADE,
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name=_("Parameter"),
        related_name="product_parameters",
        blank=True,
        on_delete=models.CASCADE,
    )
    value = models.CharField(verbose_name=_("Value"), max_length=100)

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(
                fields=["product_info", "parameter"], name="unique_product_parameter"
            ),
        ]


class Order(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        related_name="orders",
        blank=False,
        on_delete=models.CASCADE,
    )
    date_time = models.DateTimeField(auto_now_add=True)
    state = models.CharField(
        verbose_name=_("State"),
        choices=STATE_CHOICES,
        max_length=15,
    )
    contact = models.ForeignKey(
        Contact,
        verbose_name=_("Contact"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Список заказ"
        ordering = ("-date_time",)

    def __str__(self) -> str:
        return f"{self.user}: {self.date_time}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name=_("Order"),
        related_name="ordered_items",
        blank=False,
        on_delete=models.CASCADE,
    )
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name=_("Product`s information"),
        related_name="ordered_items",
        blank=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))

    class Meta:
        verbose_name = "Заказанная позиция"
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(
                fields=["order_id", "product_info"], name="unique_order_item"
            ),
        ]


class ConfirmEmailToken(models.Model):
    @staticmethod
    def generate_key() -> str:
        """generates a pseudo random code using os.urandom and binascii.hexlify"""
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name="confirm_email_tokens",
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("When was this token generated")
    )

    key = models.CharField(_("Key"), max_length=64, db_index=True, unique=True)

    def save(self, *args: Optional[tuple], **kwargs: Optional[dict]) -> None:
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Токен подтверждения Email"
        verbose_name_plural = "Токены подтверждения Email"

    def __str__(self) -> str:
        return f"Password reset token for user {self.user}"
