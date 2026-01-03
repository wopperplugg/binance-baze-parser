print("✅ Приложение 'binance_parser' успешно загружено!")

from .celery import app as celery_app

__all__ = ("celery_app",)
