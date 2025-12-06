import os
import django
from binance import AsyncClient, HistoricalKlinesType
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from .models import Kline
import asyncio
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'binance_parser.settings')
django.setup()

load_dotenv()

@sync_to_async
def save_kline_data_bulk(data):
    """Сохранение данных о свечах в базу данных пакетно."""
    Kline.objects.bulk_create([
        Kline(
            symbol=item['symbol'],
            timestamp=item['timestamp'],
            open_price=item['open_price'],
            close_price=item['close_price'],
            high_price=item['high_price'],
            low_price=item['low_price'],
            volume=item['volume']
        ) for item in data
    ], ignore_conflicts=True)
    logging.info(f"Сохранено {len(data)} свечей.")

async def fetch_historical_klines(client, symbol, interval, start_time="1 Jan 2017", end_time=None, limit=1000):
    """
    Получение исторических данных о свечах с использованием get_historical_klines.
    """
    try:
        # Преобразование времени в миллисекунды
        if isinstance(start_time, str):
            start_time = int(datetime.strptime(start_time, "%d %b %Y").timestamp() * 1000)

        all_data = []  # Список для хранения всех данных

        while True:
            # Получение данных через get_historical_klines
            klines = await client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_time,
                end_str=end_time,
                limit=limit,
                klines_type=HistoricalKlinesType.FUTURES  # Указываем тип данных: фьючерсы
            )

            if not klines:
                logging.info(f"Данные для {symbol} закончились.")
                break

            # Обработка полученных данных
            for kline in klines:
                all_data.append({
                    'symbol': symbol,
                    'timestamp': int(kline[0]),
                    'open_price': float(kline[1]),
                    'high_price': float(kline[2]),
                    'low_price': float(kline[3]),
                    'close_price': float(kline[4]),
                    'volume': float(kline[5])
                })

            logging.info(f"Получены данные для {symbol}, интервал {interval}. Последняя свеча: {datetime.fromtimestamp(klines[-1][0] / 1000)}")

            # Если данных меньше лимита, значит, они закончились
            if len(klines) < limit:
                break

            # Обновляем временную метку для следующего запроса
            start_time = int(klines[-1][0]) + 1
            await asyncio.sleep(2)  # Задержка для избежания превышения лимита API

        # Сохраняем все данные пакетно
        await save_kline_data_bulk(all_data)

    except Exception as e:
        logging.error(f"Ошибка при получении исторических данных: {e}")

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

        for symbol in symbols:
            await fetch_historical_klines(client, symbol, interval)

    except KeyboardInterrupt:
        logging.info("Парсинг остановлен пользователем")
    except Exception as e:
        logging.error(f"Ошибка при работе с API: {e}")
    finally:
        await client.close_connection()

if __name__ == "__main__":
    asyncio.run(start_websocket())