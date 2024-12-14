from django.urls import path

from autosales.views import OrderView

app_name = "autosales"
urlpatterns = [
    path("order", OrderView.as_view(), name="order"),
]
