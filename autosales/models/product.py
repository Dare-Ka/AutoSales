from django.utils.translation import gettext_lazy as _
from django.db import models

from .shop import Category, Shop


class Product(models.Model):
    objects = models.manager.Manager()
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
    objects = models.manager.Manager()
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
    objects = models.manager.Manager()
    name = models.CharField(max_length=40, verbose_name=_("Name"))

    class Meta:
        verbose_name = "Имя параметра"
        verbose_name_plural = "Список имен параметров"
        ordering = ("-name",)

    def __str__(self) -> str:
        return str(self.name)


class ProductParameter(models.Model):
    objects = models.manager.Manager()
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
