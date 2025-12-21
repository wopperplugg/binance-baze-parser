import os
import django
from binance import AsyncClient, BinanceSocketManager
from django.utils.timezone import now
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from .models import Kline, Coin
import asyncio
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "binance_parser.settings")
django.setup()

load_dotenv()


@sync_to_async
def save_kline_data(
    coin, open_price, close_price, high_price, low_price, volume, transaction_time
):
    """
    Сохранение данныхх о свечах в базу данных
    """
    coin, _ = Coin.objects.get_or_create(coin=coin)

    Kline.objects.update_or_create(
        coin=coin,
        transaction_time=transaction_time,
        defaults={
            "open_price": open_price,
            "close_price": close_price,
            "high_price": high_price,
            "low_price": low_price,
            "volume": volume,
        },
    )
    print(f"Созранена свеча для {coin}: Открвтие={open_price}, Закрытие={close_price}")


async def handle_kline_data(data):
    """
    Обработчик данных о свечах
    """
    try:
        kline_data = data["k"]
        coin = kline_data["s"].upper()
        open_price = float(kline_data["o"])
        close_price = float(kline_data["c"])
        high_price = float(kline_data["h"])
        low_price = float(kline_data["l"])
        volume = float(kline_data["v"])
        timestamp = int(kline_data["t"])
        transaction_time = datetime.fromtimestamp(int(timestamp) / 1000)
        await save_kline_data(
            coin,
            open_price,
            close_price,
            high_price,
            low_price,
            volume,
            transaction_time,
        )
    except Exception as e:
        print(f"ошибка при обработке данных о свечах: {e}")


async def start_websocket():
    """
    Запуск вебсокет для получения данных о свечах
    """
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError("API ключи не найдены в переменных окружения")

    client = await AsyncClient.create(api_key, secret_key)
    web_socket = BinanceSocketManager(client)
    try:
        symbols = ["btcusdt", "ethusdt"]
        interval = "1m"
        combined_streams = [f"{channel}@kline_{interval}" for channel in symbols]
        ticker = web_socket.multiplex_socket(combined_streams)

        async with ticker as stream:
            while True:
                res = await stream.recv()
                if "stream" in res and "data" in res:
                    data = res["data"]
                    await handle_kline_data(data)
    except KeyboardInterrupt:
        print("WebSocket остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при работе с WebSocket: {e}")
    finally:
        await client.close_connection()


if __name__ == "__main__":
    asyncio.run(start_websocket())
