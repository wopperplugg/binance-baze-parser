from django.core.management.base import BaseCommand
from coins.kline_data import start_websocket
import asyncio

class Command(BaseCommand):
    help = 'Запускает WebSocket для получения данных kline'
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Запуск WebSocket для Kline...")
        try:
            asyncio.run(start_websocket())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("WebSocket (Kline) остановлен пользоветелем"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
        finally:
            self.stdout.write(self.style.SUCCESS("Соудинение kline закрыто."))