from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from autosales.models import Shop, Category
from django.utils.translation import gettext_lazy as _


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
        )
        read_only = ("id",)

    def validate(self, attrs):
        if not attrs.get("name"):
            raise ValidationError(_("Поле 'Имя' обязательно"))
        return attrs


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = (
            "id",
            "name",
            "url",
            "user",
            "state",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        if not attrs.get("name") or not attrs.get("state"):
            raise ValidationError(_("Поля 'Имя' и 'Состояние обязательны'"))
        return attrs
