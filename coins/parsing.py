from binance.client import Client
from .models import Coin
import os
from dotenv import load_dotenv
load_dotenv()
def get_binance_coins():
    api_key = os.gotenv('BINANCE_API_KEY')
    secret_key = os.gotenv('BINANCE_API_KEY')
    
    if not api_key or not secret_key:
        raise ValueError("API ключи не найдены в переменных окружения")
    
    client = Client(api_key, secret_key)