from django.urls import path
from . import views

urlpatterns = [
    path("", views.coins, name="coins"),
    path("coin-table/", views.coin_table, name="coin_table"),
    path("<str:coin>/", views.get_klines, name="get_klines"),
]
