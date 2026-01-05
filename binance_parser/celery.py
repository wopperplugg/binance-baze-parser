import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "binance_parser.settings")

app = Celery("binance_parser")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "calculate-indicators-every-minute": {
        "task": "coins.tasks.calculate_indicators_task",
        "schedule": 5.0,
    },
}

app.conf.timezone = "UTC"
