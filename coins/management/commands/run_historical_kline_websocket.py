import asyncio
import os 
import django
from django.core.management.base import BaseCommand
from coins.historical_klines import start_websocket

class Command(BaseCommand):
    help = "Запускает вебсокет для получения исторических данных свечей "
    
    def handle(self, *args, **options):
        try:
            os.environ.setdefault('DJANGO_SETTINGS-MODULE', 'binance_parser.setting')
            django.setup()
            self.stdout.write(self.style.SUCCESS("✅ Django успешно инициализирован."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка инициализации Django: {e}"))
            return

        self.stdout.write(self.style.NOTICE("🚀 Запуск WebSocket для Kline..."))
        
        try:
            asyncio.run(start_websocket())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("WebSocket остановлен пользователем."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
        finally:
            self.stdout.write(self.style.SUCCESS("Соединение закрыто."))