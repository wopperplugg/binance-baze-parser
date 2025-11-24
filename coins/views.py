from django.shortcuts import render
from .models import Coin, Kline

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

def kline_data(request):
    kline = Kline.objects.all()
    
    symbol = request.GET.get('symbol', '').strip()
    min_timestamp = request.GET.get('min_timestamp', '').strip()
    max_timestamp = request.GET.get('max_timestamp', '').strip()
    open_price = request.GET.get('open_price', '').strip()
    close_price = request.GET.get('close_price', '').strip()
    high_price = request.GET.get('high_price', '').strip()
    low_price = request.GET.get('low_price', '').strip()
    min_volume = request.GET.get('min_volume', '').strip()
    max_volume = request.GET.get('max_volume', '').strip()
    
    if symbol:
        kline = kline.filter(symbol__icontains=symbol)
    if min_timestamp:
        try:
            kline = kline.filter(timestamp__gte=int(min_timestamp))
        except(ValueError, TypeError):
            pass
    if max_timestamp:
        try:
            kline = kline.filter(timestamp__lte=int(max_timestamp))
        except(ValueError, TypeError):
            pass
    if min_volume:
        try:
            kline = kline.filter(volume__gte=float(min_volume))
        except(ValueError, TypeError):
            pass
    if max_volume:    
        try:
            kline = kline.filter(volume__lte=float(max_volume))
        except(ValueError, TypeError):
            pass
    return render(request, 'kline_table.html', {'kline': kline})