from rest_framework.serializers import ModelSerializer, StringRelatedField
from autosales.models import Product, ProductInfo, ProductParameter


class ProductSerializer(ModelSerializer):
    categories = StringRelatedField(many=True)

    class Meta:
        model = Product
        depth = 1
        fields = ("name", "categories")


class ProductParameterSerializer(ModelSerializer):
    parameter = StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ("parameter", "value")


class ProductInfoSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameter = ProductParameterSerializer(many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = "__all__"
        read_only_fields = ("id",)
