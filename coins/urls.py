from django.urls import path
from . import views

urlpatterns = [
    path("", views.coins, name="coins"),
    path("coin-table/", views.coin_table, name="coin_table"),
    path("<str:coin>/", views.chart_page, name="chart_page"),
    path("api/klines/<str:coin>/", views.get_klines, name="get_klines_api"),
    path("api/orderbook/<str:coin>/", views.get_order_book, name="get_order_book_api"),
    path(
        "api/sentiment/<str:coin>/",
        views.get_sentiment_indicators,
        name="get_sentiment_api",
    ),
    path(
        "api/volatility/<str:coin>/",
        views.get_volatility_liquidity_indicators,
        name="get_volatility_api",
    ),
    path(
        "api/technical/<str:coin>/",
        views.get_technical_triggers,
        name="get_technical_api",
    ),
]
