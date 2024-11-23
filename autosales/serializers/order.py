from rest_framework.serializers import ModelSerializer, IntegerField
from autosales.models import Order, OrderItem
from autosales.serializers.product import ProductInfoSerializer
from autosales.serializers.user import ContactSerializer


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


class OrderSerializer(ModelSerializer):
    ordered_items = OrderItemSerializer(read_only=True, many=True)

    total_sum = IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "ordered_items",
            "state",
            "date_time",
            "total_sum",
            "contact",
        )
        read_only_fields = ("id",)
