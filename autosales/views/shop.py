from rest_framework.generics import ListAPIView

from autosales.models import Category, Shop
from autosales.serializers import CategorySerializer, ShopSerializer


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
