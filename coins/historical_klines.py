import os
import django
from binance import AsyncClient, HistoricalKlinesType
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from .models import Kline
import asyncio
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'binance_parser.settings')
django.setup()

load_dotenv()

@sync_to_async
def save_kline_data(symbol, open_price, close_price, high_price, low_price, volume, timestamp):
    """Сохранение данных о свечах в базу данных."""
    Kline.objects.update_or_create(
        symbol=symbol,
        timestamp=timestamp,
        defaults={
            'open_price': open_price,
            'close_price': close_price,
            'high_price': high_price,
            'low_price': low_price,
            'volume': volume
        }
    )
    print(f"Сохранена свеча для {symbol}: цена открытия={open_price}, цена закрытия={close_price}")

async def fetch_historical_klines(client, symbol, interval, start_time=None, end_time=None, limit=1000):
    """
    Получение исторических данных о свечах с использованием get_historical_klines.
    """
    try:
        # Преобразование времени в миллисекунды, если переданы строки
        if isinstance(start_time, str):
            start_time = int(datetime.strptime(start_time, "%d %b %Y").timestamp() * 1000)
        if isinstance(end_time, str):
            end_time = int(datetime.strptime(end_time, "%d %b %Y").timestamp() * 1000)

        # Получение данных через get_historical_klines
        klines = await client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_time,
            end_str=end_time,
            limit=limit,
            klines_type=HistoricalKlinesType.FUTURES  # Указываем тип данных: фьючерсы
        )

        # Обработка полученных данных
        for kline in klines:
            timestamp = int(kline[0])  # Временная метка открытия
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])

            await save_kline_data(symbol, open_price, close_price, high_price, low_price, volume, timestamp)

        print(f"Получены данные для {symbol} интервал {interval}")
        return klines  # Возвращаем данные для дальнейшего использования

    except Exception as e:
        print(f"Ошибка при получении исторических данных: {e}")
        return []  # Возвращаем пустой список в случае ошибки

async def start_websocket():
    """
    Основная функция для парсинга исторических данных фьючерсов.
    """
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')

    if not api_key or not secret_key:
        raise ValueError("API ключи не найдены в переменных окружения")

    client = await AsyncClient.create(api_key, secret_key)

    try:
        symbols = ['BTCUSDT', 'ETHUSDT']  # Символы фьючерсов
        interval = '1m'  # Интервал свечей (например, 1 минута)
        start_time = "1 Jan 2023"  # Начальная дата для парсинга
        end_time = "1 Feb 2023"  # Конечная дата для парсинга

        for symbol in symbols:
            current_start_time = start_time
            while True:
                klines = await fetch_historical_klines(
                    client, symbol, interval, current_start_time, end_time, limit=1000
                )

                if len(klines) < 1000:  # Если данных меньше 1000, значит, они закончились
                    break

                # Обновляем временную метку для следующего запроса
                current_start_time = int(klines[-1][0]) + 1  # Временная метка последней свечи + 1 миллисекунда
                await asyncio.sleep(10)  # Задержка для избежания превышения лимита API

    except KeyboardInterrupt:
        print("Парсинг остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при работе с API: {e}")
    finally:
        await client.close_connection()

if __name__ == "__main__":
    asyncio.run(start_websocket())