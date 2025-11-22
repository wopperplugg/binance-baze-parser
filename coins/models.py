from django.db import models
from django.utils.timezone import now

class Coin(models.Model):
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    price = models.DecimalField(max_digits=20, decimal_places=8, db_index=True)
    price_change_percent = models.DecimalField(max_digits=10, decimal_places=2, db_index=True, null=True)
    volume = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    updated_at = models.DateTimeField(default=now)
    def __str__(self):
        return self.symbol
class Kline(models.Model):
    symbol = models.CharField(max_length=20)
    timestamp = models.BigIntegerField()
    open_price = models.FloatField()
    close_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    volume = models.FloatField()
    
    class Meta:
        unique_together = ('symbol', 'timestamp')
    
    def __str__(self):
        return f"{self.symbol} - {self.timestamp}"