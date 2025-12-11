import os
import django
from binance import AsyncClient, HistoricalKlinesType
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from coins.models import Kline, Coin
import asyncio
from datetime import datetime, timezone
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'binance_parser.settings')
django.setup()

load_dotenv()

@sync_to_async
def save_kline_data_bulk(coin_name, data):
    """Сохранение данных о свечах в базу данных пакетно."""
    try:
        # Проверяем наличие монеты только один раз при старте парсинга
        coin = Coin.objects.get(coin=coin_name)
        # logging.info(f"Монета {coin_name} найдена в базе данных.") # Это лучше логировать снаружи цикла
    except Coin.DoesNotExist:
        logging.error(f"Монета {coin_name} не найдена в базе данных.")
        raise ValueError(f"Монета {coin_name} не найдена в базе данных.")

    # logging.debug(f"Данные для сохранения: {data[:5]}")

    Kline.objects.bulk_create([
        Kline(
            coin=coin,
            transaction_time=item['transaction_time'],
            open_price=item['open_price'],
            close_price=item['close_price'],
            high_price=item['high_price'],
            low_price=item['low_price'],
            volume=item['volume']
        ) for item in data
    ], ignore_conflicts=True)
    logging.info(f"Сохранено {len(data)} свечей для {coin_name}.")

async def fetch_historical_klines(client, symbol, interval, start_time="1 Jan 2017", end_time=None, limit=1000):
    try:
        # --- Добавлено: Предварительная проверка монеты ---
        try:
            # Используем sync_to_async для доступа к Django ORM вне асинхронного контекста
            await sync_to_async(Coin.objects.get)(coin=symbol)
            logging.info(f"Монета {symbol} найдена в базе данных, начинаем парсинг.")
        except Coin.DoesNotExist:
            logging.error(f"Монета {symbol} не найдена в базе данных. Пропуск.")
            return
        # -------------------------------------------------

        # Преобразование времени в миллисекунды
        if isinstance(start_time, str):
            try:
                start_time = int(datetime.strptime(start_time, "%d %b %Y").timestamp() * 1000)
            except ValueError as e:
                logging.error(f"Ошибка при парсинге даты: {e}")
                return

        while True:
            klines = await client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_time,
                end_str=end_time,
                limit=limit,
                klines_type=HistoricalKlinesType.FUTURES
            )

            if not klines:
                logging.info(f"Данные для {symbol} закончились.")
                break

            processed_data = [] # Список для хранения данных текущей партии

            for kline in klines:
                transaction_time = datetime.fromtimestamp(int(kline[0]) / 1000, tz=timezone.utc)
                data_item = {
                    'transaction_time': transaction_time,
                    'open_price': float(kline[1]),
                    'high_price': float(kline[2]),
                    'low_price': float(kline[3]),
                    'close_price': float(kline[4]),
                    'volume': float(kline[5])
                }
                processed_data.append(data_item)

            logging.info(f"Получены данные для {symbol}, интервал {interval}. Последняя свеча партии: {datetime.fromtimestamp(klines[-1][0] / 1000)}. Количество: {len(processed_data)}")

            # --- Изменено: Сохраняем данные сразу после получения ---
            if processed_data:
                await save_kline_data_bulk(symbol, processed_data)
            # ----------------------------------------------------

            if len(klines) < limit:
                break

            # Обновляем временную метку для следующего запроса (следующая свеча)
            start_time = int(klines[-1][0]) + 1
            await asyncio.sleep(1) # Уменьшил задержку, 1-2 секунды достаточно

    except Exception as e:
        logging.error(f"Ошибка при получении или сохранении данных для {symbol}: {e}")
    
    # После завершения цикла или при ошибке, функция завершается.
    logging.info(f"Парсинг исторических данных для {symbol} завершен.")


async def start_websocket():
    # ... (остальной код функции start_websocket остается без изменений) ...
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')

    if not api_key or not secret_key:
        raise ValueError("API ключи не найдены в переменных окружения")

    client = await AsyncClient.create(api_key, secret_key)

    try:
        symbols = ['BTCUSDT', 'ETHUSDT']
        interval = '1m'

        # Запускаем парсинг для каждого символа параллельно
        await asyncio.gather(*[fetch_historical_klines(client, symbol, interval) for symbol in symbols])

    except KeyboardInterrupt:
        logging.info("Парсинг остановлен пользователем")
    except Exception as e:
        logging.error(f"Ошибка при работе с API: {e}")
    finally:
        await client.close_connection()
        logging.info("Соединение с Binance API закрыто.")

if __name__ == "__main__":
    # Логирование начала процесса
    logging.info("🚀 Запуск WebSocket для Kline...")
    try:
        asyncio.run(start_websocket())
    except KeyboardInterrupt:
        logging.info("Скрипт завершен вручную.")