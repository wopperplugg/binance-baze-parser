from django.core.management.base import BaseCommand
from coins.order_book import start_websocket
import asyncio


class Command(BaseCommand):
    help = "запускает вебсокет для получения книги ордеров"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Запуск WebSocket для Order Book...")
        try:
            asyncio.run(start_websocket())
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING("WebSocket (Order Book) остановлен пользователем")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ошибка {e}"))
        finally:
            self.stdout.write(self.style.SUCCESS("Соединение Order Book закрыто."))
