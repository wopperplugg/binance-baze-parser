from celery import shared_task
from django.core.management import call_command


@shared_task
def calculate_indicators_task():
    """
    selery task для калькуляции индикаторов и импорта в базу данных
    """
    try:
        call_command("calculate_indicators", limit=100)
        return "калькуляция индикатора закончилась успешно"
    except Exception as e:
        return f"ошибка калькуляции индикаторов {str(e)}"
