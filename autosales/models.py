from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.db import models

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
        self, email: str, password: str | None = None, **extra_fields: Any
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
        self, email: str, password: str, **extra_fields: Any
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

    def __str__(self):
        return self.name


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
