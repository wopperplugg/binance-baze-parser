from django.urls import path
from . import views

urlpatterns = [
    path("", views.coins, name="coins"),
    path("coin-table/", views.coin_table, name="coin_table"),
    path("<str:coin>/", views.chart_page, name="chart_page"),
    path("api/klines/<str:coin>/", views.get_klines, name="get_klines_api"),
    path("api/orderbook/<str:coin>/", views.get_order_book, name="get_order_book_api"),
]
