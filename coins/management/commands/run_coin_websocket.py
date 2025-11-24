from django.core.management.base import BaseCommand
from coins.coin_table import start_websocket 
import asyncio

class Command(BaseCommand):
    help = 'Запускает WebSocket для получения данных с Binance'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Запуск WebSocket...")
        try:
            asyncio.run(start_websocket())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("WebSocket остановлен пользователем."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
        finally:
            self.stdout.write(self.style.SUCCESS("Соединение закрыто."))