from celery import shared_task
from django.core.management import call_command


@shared_task
def calculate_indicators_task(limit=100, batch_size=10):
    """
    selery task для калькуляции индикаторов и импорта в базу данных
    """
    try:
        for offset in range(0, limit, batch_size):
            call_command("calculate_indicators", limit=batch_size, offset=offset)
            print(f"Обработана партия данных: offset={offset}, batch_size={batch_size}")
        return "калькуляция индикатора закончилась успешно"
    except Exception as e:
        return f"ошибка калькуляции индикаторов {str(e)}"
