from rest_framework.generics import ListAPIView
from django.db.models import Q
from rest_framework.response import Response

from autosales.models import ProductInfo
from autosales.serializers import ProductInfoSerializer


class ProductInfoView(ListAPIView):
    def list(self, request, *args, **kwargs):
        query = Q(shop__state=True)
        shop_id = request.query_params.get("shop_id")
        category_id = request.query_params.get("category_id")

        if shop_id:
            query = query & Q(shop_id=shop_id)
        if category_id:
            query = query & Q(category_id=category_id)

        queryset = (
            ProductInfo.objects.filter(query)
            .select_related("shop", "product__category")
            .prefetch_related("product_parameters__parameter")
            .distinct()
        )
        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)
