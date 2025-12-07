from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET
from dateutil.parser import parse as parse_date
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

    return render(request, "coin_table.html", {"coins": coins})


RES_MAP = {
    "1m": "coins_kline",
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
        return render(request, "kline_chart.html", {"error": "Coin is required"})

    resolution = request.GET.get("resolution", "1m")
    table = RES_MAP.get(resolution)
    if not table:
        return render(request, "kline_chart.html", {"error": "Invalid resolution"})

    start = request.GET.get("start")
    end = request.GET.get("end")

    # Ограничиваем максимальное значение limit
    limit = min(int(request.GET.get("limit", 500)), 1000)

    # Проверяем существование монеты (регистронезависимо)
    coin_obj = get_object_or_404(Coin, coin__iexact=coin)

    # Формируем SQL-запрос
    params = [str(coin_obj.id)]  # Преобразуем coin_obj.id в строку
    where_clauses = ["coin_id = %s"]

    time_col = '"transaction_time"' if table == "coins_kline" else "bucket"

    if start:
        try:
            start_date = parse_date(start)
            where_clauses.append(f"{time_col} >= %s")
            params.append(start_date)
        except ValueError:
            return render(request, "kline_chart.html", {"error": "Invalid start date format"})
    if end:
        try:
            end_date = parse_date(end)
            where_clauses.append(f"{time_col} <= %s")
            params.append(end_date)
        except ValueError:
            return render(request, "kline_chart.html", {"error": "Invalid end date format"})

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
            "ts": r[0].isoformat() if hasattr(r[0], "isoformat") else str(r[0]),
            "open": float(r[1]) if r[1] is not None else None,
            "high": float(r[2]) if r[2] is not None else None,
            "low": float(r[3]) if r[3] is not None else None,
            "close": float(r[4]) if r[4] is not None else None,
            "volume": float(r[5]) if r[5] is not None else None,
        }
        for r in rows
    ]

    context = {
        "coin": coin_obj.coin,
        "resolution": resolution,
        "chart_data": data,  # Передаем данные для графика
    }

    return render(request, "kline_chart.html", context)