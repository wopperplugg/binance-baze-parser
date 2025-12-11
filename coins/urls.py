from django.urls import path
from . import views

urlpatterns = [
    path("", views.coins, name="coins"),
    path("coin-table/", views.coin_table, name="coin_table"),
    path("<str:coin>/", views.coin_chart_page, name="coin_chart_page"),
    path("api/klines/<str:coin>/", views.get_klines, name="get_klines_api"),
]
