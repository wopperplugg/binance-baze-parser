from django.shortcuts import render
from .models import Coin

def coins(request):
    return render(request, 'coins.html')

def coin_table(request):
    coins = Coin.objects.all()
    
    symbol = request.GET.get('symbol', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    price_change = request.GET.get('price_change', '').strip()
    
    if symbol:
        coins = coins.filter(symbol__icontains=symbol)
    if min_price:
        try:
            coins = coins.filter(price__gte=float(min_price)) 
        except(ValueError, TypeError):
            pass
    if max_price:
        try:
            coins = coins.filter(price__lte=float(max_price))
        except(ValueError, TypeError):
            pass
    if price_change:
        try:
            price_change = float(price_change)
            if price_change > 0:
                coins = coins.filter(price_change_percent__gt=0)
            elif price_change < 0:
                coins = coins.filter(price_change_percent__lt=0)
        except (ValueError, TypeError):
            pass
        
    return render(request, 'coin_table.html', {'coins': coins})