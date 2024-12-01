from time import process_time

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, StringRelatedField
from autosales.models import Product, ProductInfo, ProductParameter
from django.utils.translation import gettext_lazy as _


class ProductSerializer(ModelSerializer):
    categories = StringRelatedField(many=True)

    class Meta:
        model = Product
        depth = 1
        fields = ("name", "categories")

    def validate(self, attrs):
        if not attrs.get("name"):
            raise ValidationError(_("Поле 'Имя' обязательно"))
        return attrs


class ProductParameterSerializer(ModelSerializer):
    parameter = StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ("parameter", "value")

    def validate(self, attrs):
        if not attrs.get("value"):
            raise ValidationError(_("Поле 'Значение' обязательно"))
        return attrs


class ProductInfoSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameter = ProductParameterSerializer(many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = (
            "id",
            "external_id",
            "model",
            "product",
            "shop",
            "quantity",
            "price",
            "price_rrc",
            "product_parameters",
        )
        read_only_fields = ("id",)

    def validate_external_id(self, external_id):
        if not external_id:
            raise ValidationError(_("Поле 'Внешний ID' является обязательным"))
        if external_id <= 0:
            raise ValidationError(_("Внешний ID должен быть числом больше 0"))
        return external_id

    def validate_quantity(self, quantity):
        if not quantity:
            raise ValidationError(_("Поле 'Количество' является обязательным"))
        if quantity <= 0:
            raise ValidationError(_("Количество должно быть числом больше 0"))
        return quantity

    def validate_price(self, price):
        if not price:
            raise ValidationError(_("Поле 'Цена' является обязательным"))
        if price <= 0:
            raise ValidationError(_("Цена должна быть числом больше 0"))
        return price

    def validate_price_rrc(self, price_rcc):
        if not price_rcc:
            raise ValidationError(
                _("Поле 'Рекомендуемая розничная цена' является обязательным")
            )
        if price_rcc <= 0:
            raise ValidationError(_("Розничная цена должна быть числом больше 0"))
        return price_rcc
