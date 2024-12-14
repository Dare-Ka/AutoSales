from django.db import IntegrityError
from django.db.models import Sum, F
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response

from autosales.models import Order
from autosales.serializers import OrderSerializer
from autosales.signals.signals import new_user_registered, new_order


class OrderView(ListAPIView, CreateAPIView):
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        order = (
            Order.objects.filter(user_id=request.user.id)
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

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"Status": False, "Error": "Log in required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if {"id", "contact"}.issubset(request.data):
            if request.data["id"].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data["id"]
                    ).update(contact_id=request.data["contact"], state="new")
                except IntegrityError as error:
                    print(error)
                    return Response(
                        {"Status": False, "Errors": "Неправильно указаны аргументы"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                else:
                    if is_updated:
                        new_order.send(sender=self.__class__, user_id=request.user.id)
                        return Response({"Status": True}, status=status.HTTP_200_OK)

        return Response(
            {"Status": False, "Errors": "Не указаны все необходимые аргумент"},
            status=status.HTTP_403_FORBIDDEN,
        )
