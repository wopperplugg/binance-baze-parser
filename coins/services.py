from datetime import datetime
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from .models import Coin
from .constants import RES_MAP


def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise ValueError("Invalid date format")
    
def fetch_klines_data(coin, resolution, start=None, end=None, limit=500):
    table = RES_MAP.get(resolution)
    if not table:
        raise ValueError("Invalid resolution")
    
    try:
        coin_obj = Coin.objects.get(coin__iexact=coin)
    except ObjectDoesNotExist:
        raise ValueError("Coin not found")
    
    params = [str(coin_obj.coin)]
    where_clauses = ["coin_id = %s"]

    time_col = "bucket"

    if start:
        start_date = parse_date(start)
        where_clauses.append(f"{time_col} >= %s")
        params.append(start_date)
    
    if end:
        end_date = parse_date(end)
        where_clauses.append(f"{time_col} <= %s")
        params.append(end_date)
    
    where_sql = " AND ".join(where_clauses)

    sql = f"""
    SELECT {time_col} AS ts, open_price, high_price, low_price, close_price, volume
    FROM {table}
    WHERE {where_sql}
    ORDER BY ts DESC
    LIMIT %s;
    """

    params.append(limit)

    with connection.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    
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

    return {
        "coin": coin_obj.coin,
        "resolution": resolution,
        "data": data,
    }