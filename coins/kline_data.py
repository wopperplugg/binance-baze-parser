import os 
import django 
from binance import AsyncClient, BinanceSocketManager
from django.utils.timezone import now
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from .models import Kline
import asyncio
import json

os.environ.setdefaul('DJANGO_SETTINGS_MOSULE', 'binance_parser.settings')
django.setup()

load_dotenv()

@sync_to_async
def save_kline_data(symbol, open_price, close_price, high_price, low_price, volume, timestamp):
    """ 
    Сохранение данныхх о свечах в базу данных
    """
    Kline.objects.update_or_create(
        symbol=symbol,
        timestamp=timestamp,
        defaults={
            'open_price' :open_price,
            'close_price': close_price,
            'high_price': high_price,
            'low_price': low_price,
            'volume': volume
        }
    )
    print(f"Созранена свеча для {symbol}: Открвтие={open_price}, Закрытие={close_price}")
    
async def handle_kline_data(data):
    """
    Обработчик данных о свечах
    """    
    try:
        kline_data = data['k']
        symbol = kline_data['s']
        open_price = float(kline_data['o'])
        close_price = float(kline_data['c'])
        high_price = float(kline_data['h'])
        low_price = float(kline_data['l'])
        volume = float(kline_data['v'])
        timestamp = int(kline_data['t'])
        
        await save_kline_data(symbol, open_price, close_price, high_price, low_price, volume, timestamp)
    except Exception as e:
        print(f"ошибка при обработке данных о свечах: {e}")
        
async def start_websocket():
    """
    Запуск вебсокет для получения данных о свечах 
    """
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    if not api_key or not secret_key:
        raise ValueError("API ключи не найдены в переменных окружения")
    
    client = await AsyncClient.create(api_key, secret_key)
    web_socket = BinanceSocketManager(client)
    try:
        # Подписка на свечи для вех пар интервал 4 часа
        channels = ['@kline_4h'] 
        combined_streams = [f"{channel}" for channel in channels]
        ticker = web_socket.multiplex_socket(combined_streams)
    except KeyboardInterrupt:
        print("WebSocket остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при работе с WebSocket: {e}")
    finally:
        await client.close_connection()
if __name__ == "__main__":
    asyncio.run(start_websocket())
    