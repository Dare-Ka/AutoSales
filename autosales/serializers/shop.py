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
