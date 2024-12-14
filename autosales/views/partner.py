from distutils.util import strtobool

from django.core.validators import URLValidator
from django.db.models import Sum, F
from requests import get
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response

from autosales.models import (
    Category,
    ProductInfo,
    Product,
    Shop,
    Parameter,
    ProductParameter,
    Order,
)
from autosales.serializers import ShopSerializer, OrderSerializer


class PartnerUpdate(CreateAPIView):
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"Status": False, "Error": "Log in required"}, status=403)

        if request.user.type != "shop":
            return Response(
                {"Status": False, "Error": "Только для магазинов"}, status=403
            )

        url = request.data.get("url")
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return Response({"Status": False, "Error": str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)

                shop, _ = Shop.objects.get_or_create(
                    name=data["shop"], user_id=request.user.id
                )
                for category in data["categories"]:
                    category_object, _ = Category.objects.get_or_create(
                        id=category["id"], name=category["name"]
                    )
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data["goods"]:
                    product, _ = Product.objects.get_or_create(
                        name=item["name"], category_id=item["category"]
                    )

                    product_info = ProductInfo.objects.create(
                        product_id=product.id,
                        external_id=item["id"],
                        model=item["model"],
                        price=item["price"],
                        price_rrc=item["price_rrc"],
                        quantity=item["quantity"],
                        shop_id=shop.id,
                    )
                    for name, value in item["parameters"].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(
                            product_info_id=product_info.id,
                            parameter_id=parameter_object.id,
                            value=value,
                        )

                return Response({"Status": True})

        return Response(
            {"Status": False, "Errors": "Не указаны все необходимые аргументы"}
        )


class PartnerState(CreateAPIView, RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.type != "shop":
            return Response(
                {"Status": False, "Error": "Только для магазинов"},
                status=status.HTTP_403_FORBIDDEN,
            )

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.type != "shop":
            return Response(
                {"Status": False, "Error": "Только для магазинов"},
                status=status.HTTP_403_FORBIDDEN,
            )
        state = request.data.get("state")
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(
                    state=strtobool(state)
                )
                return Response({"Status": True})
            except ValueError as error:
                return Response({"Status": False, "Errors": str(error)})

        return Response(
            {"Status": False, "Errors": "Не указаны все необходимые аргументы"}
        )


class PartnerOrders(ListAPIView):
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.type != "shop":
            return Response(
                {"Status": False, "Error": "Только для магазинов"},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = (
            Order.objects.filter(
                ordered_items__product_info__shop__user_id=request.user.id
            )
            .exclude(state="basket")
            .prefetch_related(
                "ordered_items__product_info__product__category",
                "ordered_items__product_info__product_parameters__parameter",
            )
            .select_related("contact")
            .annotate(
                total_sum=Sum(
                    F("ordered_items__quantity")
                    * F("ordered_items__product_info__price")
                )
            )
            .distinct()
        )

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
