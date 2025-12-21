import os
import django
from binance import AsyncClient, BinanceSocketManager
from django.utils.timezone import now
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from .models import OrderBook, Coin
import asyncio
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "binance_parser.settings")
django.setup()

load_dotenv()


@sync_to_async
def save_orderbook_data(symbol, bids, asks, timestamp):
    """
    сохранение данных стакана цен в базу данных
    """
    coin, _ = Coin.objects.get_or_create(coin=symbol)

    OrderBook.objects.create(
        coin=coin,
        transaction_time=timestamp,
        bids=bids,
        asks=asks,
    )
    print(f"сохранен стакан для {symbol} {timestamp}")


async def handle_orderbook_data(data):
    """
    обряботчик данных стакана цен
    """
    try:
        bids = data.get("b", [])
        asks = data.get("a", [])
        timestamp = int(data.get("E", 0))
        if not timestamp:
            raise ValueError("Timestamp отсутствует в данных")
        transaction_time = datetime.fromtimestamp(int(timestamp) / 1000)
        symbol = data.get("s", "").upper()
        await save_orderbook_data(symbol, bids, asks, transaction_time)
    except Exception as e:
        print(f"ошибка при обработке данных стакана {e}")


async def start_websocket():
    """
    запуск вебсокет для получения данных о стакане цен
    """
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError("API ключи не найдены в переменных окружения")

    client = await AsyncClient.create(api_key, secret_key)
    web_socket = BinanceSocketManager(client)

    try:
        symbol = ["btcusdt", "ethusdt"]
        combined_streams = [f"{symbol.lower()}@depth" for symbol in symbol]
        orderbook_stream = web_socket.multiplex_socket(combined_streams)

        async with orderbook_stream as stream:
            while True:
                res = await stream.recv()
                if "stream" in res and "data" in res:
                    data = res["data"]
                    await handle_orderbook_data(data)
    except KeyboardInterrupt:
        print("WebSocket остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при работе с WebSocket: {e}")
    finally:
        await client.close_connection()


if __name__ == "__main__":
    asyncio.run(start_websocket())
