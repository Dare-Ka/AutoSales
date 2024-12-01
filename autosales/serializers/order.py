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

    def validate(self, attrs):
        if not attrs.get("order") or not attrs.get("quantity"):
            raise ValidationError(_("Поля 'Заказ' и 'Количество' обязательны"))
        return attrs


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
