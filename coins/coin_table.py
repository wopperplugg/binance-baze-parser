import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'binance_parser.settings')
django.setup()

from binance import BinanceSocketManager, AsyncClient
from django.utils.timezone import now
from dotenv import load_dotenv
from .models import Coin
import json 
import asyncio
from asgiref.sync import sync_to_async

load_dotenv()



@sync_to_async
def save_coin_data(symbol, price, price_change_percent, volume):
    """ 
    Синхронная функция для сохранения данных в базу данных
    """
    Coin.objects.update_or_create(
        symbol=symbol,
        defaults={
            'price': price,
            'price_change_percent': price_change_percent,
            'volume': volume,
            'updated_at': now()
        }
    )
    print(f"Обновлены данные для монеты: {symbol}, Цена{price},  Изменение {price_change_percent}, Обьем {volume}")



async def handle_socket_message(messages):
    """
    Обработчик сообщений от вебсокет 
    """
    try:
        for msg in messages:
            if 's' in msg and 'c' in msg:
                symbol = msg['s']
                price = msg['c']
                price_change_percent = float(msg.get('P', 0.0))
                volume = float(msg.get('v', 0.0))
                
                await save_coin_data(symbol, price, price_change_percent, volume)
                
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        
     
        
async def start_websocket():
    """
    Запуск вебсокет для получения данных о монетах
    """
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    if not api_key or not secret_key:
        raise ValueError("API ключи не найдены в переменных окружения")
    
    client = await AsyncClient.create(api_key, secret_key)
    web_socket = BinanceSocketManager(client)
    try:
        ticker = web_socket.multiplex_socket(['!ticker@arr'])
        async with ticker as stream:
            while True:
                res = await stream.recv()
                if 'data' in res:
                    await handle_socket_message(res['data'])
    except KeyboardInterrupt:
        print("WebSocket остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при работе с WebSocket: {e}")
    finally:
        await client.close_connection()
