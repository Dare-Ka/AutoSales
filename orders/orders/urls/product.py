from django.urls import path

from autosales.views import ProductInfoView, BasketView

app_name = "autosales"
urlpatterns = [
    path("products", ProductInfoView.as_view(), name="shops"),
    path("basket", BasketView.as_view(), name="basket"),
]
