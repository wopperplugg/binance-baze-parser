from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Coin
from .services import fetch_klines_data, fetch_order_book_data, validate_coin_and_limit
from .constants import RES_MAP


def coins(request):
    return render(request, "coins.html")


def coin_table(request):
    coins = Coin.objects.all()

    coin = request.GET.get("coin", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    price_change = request.GET.get("price_change", "").strip()

    if coin:
        coins = coins.filter(coin__icontains=coin)
    if min_price:
        try:
            coins = coins.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            coins = coins.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
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

    paginator = Paginator(coins, 10)
    page_number = request.GET.get("page")

    try:
        coins_page = paginator.page(page_number)
    except PageNotAnInteger:
        coins_page = paginator.page(1)
    except EmptyPage:
        coins_page = paginator.page(paginator.num_pages)

    return render(request, "coin_table.html", {"coins": coins_page})


@require_GET
def get_klines(request, coin):
    coin_obj, limit = validate_coin_and_limit(request, coin)
    if isinstance(limit, JsonResponse):
        return limit

    resolution = request.GET.get("resolution", "1m")
    if resolution not in RES_MAP:
        return JsonResponse({"error": "Invalid resolution"}, status=400)

    try:
        data = fetch_klines_data(coin_obj.coin, resolution, limit=limit)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error", "details": str(e)}, status=500
        )


@require_GET
def get_order_book(request, coin):
    coin_obj, limit = validate_coin_and_limit(request, coin)
    if isinstance(limit, JsonResponse):
        return limit

    try:
        data = fetch_order_book_data(coin_obj.coin, limit=limit)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error", "details": str(e)}, status=500
        )


def chart_page(request, coin):
    coin_obj = get_object_or_404(Coin, coin__iexact=coin)
    resolution = request.GET.get("resolution", "1m")
    context = {
        "coin": coin_obj.coin,
        "resolution": resolution,
    }
    return render(request, "combined_chart.html", context)
