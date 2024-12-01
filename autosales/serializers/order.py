from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, IntegerField
from autosales.models import Order, OrderItem
from .product import ProductInfoSerializer
from .user import ContactSerializer
from django.utils.translation import gettext_lazy as _


class OrderItemSerializer(ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_info",
            "quantity",
            "order",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"order": {"write_only": True}}

    def validate_order(self, order):
        if not order:
            raise ValidationError(_("Поле 'Заказ' является обязательным"))
        return order

    def validate_quantity(self, quantity):
        if not quantity:
            raise ValidationError(_("Полу 'Количество' является обязательным"))
        if quantity <= 0:
            raise ValidationError(_("Количество должно быть числом больше 0"))
        return quantity


class OrderSerializer(ModelSerializer):
    ordered_items = OrderItemSerializer(read_only=True, many=True)

    total_sum = IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "ordered_items",
            "state",
            "date_time",
            "total_sum",
            "contact",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        if not attrs.get("user") or not attrs.get("state") or not attrs.get("contact"):
            raise ValidationError(
                _("Поля 'Пользователь', 'Состояние' и 'Контакты' обязательны")
            )
        return attrs
