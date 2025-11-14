from django.urls import path
from . import views
urlpatterns = [
    path('coins/', views.coins, name='coins'),
]