from django.core.management.base import BaseCommand
import time
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'ждем подключение к базе данных'
    
    def handle(self, *args, **oprions):
        self.stdout.write("ждем базу данных...")
        db_conn = None
        while not db_conn:
            try:
                connections['default'].cursor()
                db_conn = True
            except OperationalError:
                self.stdout.write("база данных недоступна, подождите 1 секунду...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("база данных готова"))