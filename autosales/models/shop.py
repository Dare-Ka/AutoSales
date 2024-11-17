from django.utils.translation import gettext_lazy as _
from django.db import models

from .user import User


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
