from django.urls import path

from autosales.views import CategoryView, ShopView

app_name = "autosales"
urlpatterns = [
    path("categories", CategoryView.as_view(), name="categories"),
    path("shops", ShopView.as_view(), name="shops"),
]
