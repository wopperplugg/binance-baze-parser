from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import (
    Coin,
    SentimentIndicator,
    VolatilityLiquidityIndicator,
    TechnicalTrigger,
)
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


@require_GET
def get_sentiment_indicators(request, coin):
    coin_obj = get_object_or_404(Coin, coin__iexact=coin)
    limit = request.GET.get("limit", "100")

    try:
        limit = int(limit)
        if limit <= 0:
            limit = 100
    except (ValueError, TypeError):
        limit = 100

    # Получаем последние данные
    indicators = SentimentIndicator.objects.filter(coin=coin_obj).order_by(
        "-transaction_time"
    )[:limit]

    data = []
    for indicator in indicators:
        data.append(
            {
                "transaction_time": indicator.transaction_time.isoformat(),
                "open_interest": (
                    float(indicator.open_interest) if indicator.open_interest else None
                ),
                "open_interest_change": (
                    float(indicator.open_interest_change)
                    if indicator.open_interest_change
                    else None
                ),
                "funding_rate": (
                    float(indicator.funding_rate) if indicator.funding_rate else None
                ),
                "next_funding_time": (
                    indicator.next_funding_time.isoformat()
                    if indicator.next_funding_time
                    else None
                ),
                "long_short_ratio": (
                    float(indicator.long_short_ratio)
                    if indicator.long_short_ratio
                    else None
                ),
                "long_positions": (
                    float(indicator.long_positions)
                    if indicator.long_positions
                    else None
                ),
                "short_positions": (
                    float(indicator.short_positions)
                    if indicator.short_positions
                    else None
                ),
                "created_at": indicator.created_at.isoformat(),
            }
        )

    return JsonResponse(data, safe=False)


@require_GET
def get_volatility_liquidity_indicators(request, coin):
    coin_obj = get_object_or_404(Coin, coin__iexact=coin)
    limit = request.GET.get("limit", "100")

    try:
        limit = int(limit)
        if limit <= 0:
            limit = 100
    except (ValueError, TypeError):
        limit = 100

    # Получаем последние данные
    indicators = VolatilityLiquidityIndicator.objects.filter(coin=coin_obj).order_by(
        "-transaction_time"
    )[:limit]

    data = []
    for indicator in indicators:
        data.append(
            {
                "transaction_time": indicator.transaction_time.isoformat(),
                "atr_14": float(indicator.atr_14) if indicator.atr_14 else None,
                "atr_21": float(indicator.atr_21) if indicator.atr_21 else None,
                "vwap": float(indicator.vwap) if indicator.vwap else None,
                "vwap_high_band": (
                    float(indicator.vwap_high_band)
                    if indicator.vwap_high_band
                    else None
                ),
                "vwap_low_band": (
                    float(indicator.vwap_low_band) if indicator.vwap_low_band else None
                ),
                "liquidation_levels": indicator.liquidation_levels,
                "created_at": indicator.created_at.isoformat(),
            }
        )

    return JsonResponse(data, safe=False)


@require_GET
def get_technical_triggers(request, coin):
    coin_obj = get_object_or_404(Coin, coin__iexact=coin)
    limit = request.GET.get("limit", "100")

    try:
        limit = int(limit)
        if limit <= 0:
            limit = 100
    except (ValueError, TypeError):
        limit = 100

    # Получаем последние данные
    indicators = TechnicalTrigger.objects.filter(coin=coin_obj).order_by(
        "-transaction_time"
    )[:limit]

    data = []
    for indicator in indicators:
        data.append(
            {
                "transaction_time": indicator.transaction_time.isoformat(),
                "ema_20": float(indicator.ema_20) if indicator.ema_20 else None,
                "ema_50": float(indicator.ema_50) if indicator.ema_50 else None,
                "ema_100": float(indicator.ema_100) if indicator.ema_100 else None,
                "ema_200": float(indicator.ema_200) if indicator.ema_200 else None,
                "stoch_rsi_k": (
                    float(indicator.stoch_rsi_k) if indicator.stoch_rsi_k else None
                ),
                "stoch_rsi_d": (
                    float(indicator.stoch_rsi_d) if indicator.stoch_rsi_d else None
                ),
                "volume_profile_nodes": indicator.volume_profile_nodes,
                "created_at": indicator.created_at.isoformat(),
            }
        )

    return JsonResponse(data, safe=False)
