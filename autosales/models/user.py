from typing import Optional

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


USER_TYPE_CHOICES = (
    ("shop", "Магазин"),
    ("buyer", "Покупатель"),
)


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
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]
    objects = UserManager()
    USERNAME_FIELD = "email"
    email = models.EmailField(verbose_name=_("Email address"), unique=True)
    company = models.CharField(verbose_name=_("Company"), max_length=40, blank=True)
    position = models.CharField(verbose_name=_("Position"), max_length=40, blank=True)
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
    phone = PhoneNumberField(region="RU", max_length=12, verbose_name=_("Phone number"))

    class Meta:
        verbose_name = "Контакты пользователя"
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self) -> str:
        return f"{self.user}:{self.city} {self.street} {self.house}"
