from django.db import IntegrityError
from django.db.models import Sum, F, Q
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from ujson import loads as load_json

from autosales.models import Order, OrderItem
from autosales.serializers import OrderSerializer, OrderItemSerializer


class BasketView(ModelViewSet):
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        basket = (
            Order.objects.filter(user_id=request.user.id, state="basket")
            .prefetch_related(
                "ordered_items__product_info__product__category",
                "ordered_items__product_info__product_parameters__parameter",
            )
            .annotate(
                total_sum=Sum(
                    F("ordered_items__quantity")
                    * F("ordered_items__product_info__price")
                )
            )
            .distinct()
        )
        serializer = OrderSerializer(basket, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        items_sting = request.data.get("items")
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return Response({"Status": False, "Errors": "Неверный формат запроса"})
            else:
                basket, _ = Order.objects.get_or_create(
                    user_id=request.user.id, state="basket"
                )
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({"order": basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return Response({"Status": False, "Errors": str(error)})
                        else:
                            objects_created += 1

                    else:

                        return Response({"Status": False, "Errors": serializer.errors})

                return Response(
                    {"Status": True, "Создано объектов": objects_created},
                    status=status.HTTP_200_OK,
                )
        return Response(
            {"Status": False, "Errors": "Не указаны все необходимые аргументы"}
        )

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        items_sting = request.data.get("items")
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return Response({"Status": False, "Errors": "Неверный формат запроса"})
            else:
                basket, _ = Order.objects.get_or_create(
                    user_id=request.user.id, state="basket"
                )
                objects_updated = 0
                for order_item in items_dict:
                    if (
                        type(order_item["id"]) == int
                        and type(order_item["quantity"]) == int
                    ):
                        objects_updated += OrderItem.objects.filter(
                            order_id=basket.id, id=order_item["id"]
                        ).update(quantity=order_item["quantity"])

                return Response({"Status": True, "Обновлено объектов": objects_updated})
        return Response(
            {"Status": False, "Errors": "Не указаны все необходимые аргументы"}
        )

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        items_sting = request.data.get("items")
        if items_sting:
            items_list = items_sting.split(",")
            basket, _ = Order.objects.get_or_create(
                user_id=request.user.id, state="basket"
            )
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return Response(
                    {"Status": True, "Удалено объектов": deleted_count},
                    status=status.HTTP_200_OK,
                )
        return Response(
            {"Status": False, "Errors": "Не указаны все необходимые аргументы"}
        )
