from django.urls import path
from . import views
urlpatterns = [
    path('coins/', views.coins, name='coins'),
    path('coin-table/', views.coin_table, name='coin_table'),
    path('api/klines/', views.get_klines, name='get_klines'),
]