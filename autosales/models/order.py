from django.utils.translation import gettext_lazy as _
from django.db import models

from .user import User, Contact
from .product import ProductInfo

STATE_CHOICES = (
    ("basket", "Статус корзины"),
    ("new", "Новый"),
    ("confirmed", "Подтвержден"),
    ("assembled", "Собран"),
    ("sent", "Отправлен"),
    ("delivered", "Доставлен"),
    ("canceled", "Отменен"),
)


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
