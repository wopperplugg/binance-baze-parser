from django.urls import path
from . import views
urlpatterns = [
    path('coins/', views.coins, name='coins'),
    path('coin-table/', views.coin_table, name='coin_table'),
    path('kline-table/', views.kline_data, name='kline_table'),
    path('chart/<str:symbol>/', views.kline_chart, name='kline_chart'),
]