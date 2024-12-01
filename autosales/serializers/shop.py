from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from autosales.models import Shop, Category


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
        )
        read_only = ("id",)

    def validate(self, attrs):
        if not attrs["name"]:
            raise ValidationError("Поле 'Имя' обязательно")
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
        if attrs["name"] or attrs["state"] is None:
            raise ValidationError("Поля 'Имя' и 'Состояние обязательны'")
