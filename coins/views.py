from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.views.decorators.http import require_GET
from dateutil.parser import parse as parse_date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Coin


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


RES_MAP = {
    "1m": "coins_kline_1m",
    "5m": "coins_kline_5m",
    "15m": "coins_kline_15m",
    "1h": "coins_kline_1h",
    "4h": "coins_kline_4h",
    "1d": "coins_kline_1d",
}


@require_GET
def get_klines(request, coin):
    """
    GET params:
      resolution=1m|5m|15m|1h|4h|1d (default 1m)
      start=ISO8601 optional
      end=ISO8601 optional
      limit=int optional (defaults to 500)
    """
    if not coin:
        return JsonResponse({"error": "Coin is required"}, status=400)
    try:
        limit = min(int(request.GET.get("limit", 500)), 1000)
    except ValueError:
        return JsonResponse({"error": "Invalid resolution"}, status=400)

    resolution = request.GET.get("resolution", "1m")
    table = RES_MAP.get(resolution)
    if not table:
        return JsonResponse({"error": "Invalid resolution"}, status=400)

    start = request.GET.get("start")
    end = request.GET.get("end")

    # Проверяем существование монеты (регистронезависимо)
    coin_obj = get_object_or_404(Coin, coin__iexact=coin)

    # Формируем SQL-запрос
    params = [str(coin_obj.coin)]  # Преобразуем coin_obj.id в строку
    where_clauses = ["coin_id = %s"]

    time_col = '"transaction_time"' if table == "coins_kline" else "bucket"

    if start:
        try:
            start_date = parse_date(start)
            where_clauses.append(f"{time_col} >= %s")
            params.append(start_date)
        except ValueError:
            return JsonResponse({"error": "Invalid end date format"}, status=400)
    if end:
        try:
            end_date = parse_date(end)
            where_clauses.append(f"{time_col} <= %s")
            params.append(end_date)
        except ValueError:
            return JsonResponse({"error": "Invalid end date format"}, status=400)

    where_sql = " AND ".join(where_clauses)

    sql = f"""
    SELECT {time_col} AS ts, open_price, high_price, low_price, close_price, volume
    FROM {table}
    WHERE {where_sql}
    ORDER BY ts DESC
    LIMIT %s;
    """
    params.append(limit)

    # Выполняем запрос
    with connection.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    # Форматируем данные
    rows = list(reversed(rows))
    data = [
        {
            # Используем .isoformat() напрямую для объекта datetime
            "time": r[0],
            "open": float(r[1]) if r[1] is not None else 0,
            "high": float(r[2]) if r[2] is not None else 0,
            "low": float(r[3]) if r[3] is not None else 0,
            "close": float(r[4]) if r[4] is not None else 0,
            "volume": float(r[5]) if r[5] is not None else 0,
        }
        for r in rows
    ]

    return JsonResponse(
        {
            "coin": coin_obj.coin,
            "resolution": resolution,
            "data": data,
        }
    )


def coin_chart_page(request, coin):
    coin_obj = get_object_or_404(Coin, coin__iexact=coin)
    resolution = request.GET.get("resolution", "1m")
    table = RES_MAP.get(resolution)
    context = {
        "coin": coin_obj.coin,
        "resolution": resolution,
    }
    return render(request, "kline_chart.html", context)
