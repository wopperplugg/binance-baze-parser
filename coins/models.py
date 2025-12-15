from django.db import models
from django.utils import timezone


class Coin(models.Model):
    coin = models.CharField(max_length=20, unique=True, db_index=True)
    price = models.FloatField(null=True)
    price_change_percent = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.coin


class Kline(models.Model):
    pk = models.CompositePrimaryKey("coin_id", "transaction_time")
    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="kline_data",
        db_index=True,
        to_field="coin",
    )
    transaction_time = models.DateTimeField(db_index=True)

    open_price = models.FloatField()
    close_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    volume = models.FloatField()

    class Meta:
        db_table = "coins_kline"
        constraints = [
            models.UniqueConstraint(
                fields=["coin", "transaction_time"], name="kline_primary_key"
            )
        ]
        indexes = [
            models.Index(fields=["coin", "-transaction_time"], name="kline_coin_ts_idx")
        ]

    def __str__(self):
        return f"{self.coin.coin} - {self.transaction_time.isoformat()}"


class OrderBook(models.Model):
    pk = models.CompositePrimaryKey("coin_id", "transaction_time")
    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="order_book",
        db_index=True,
        to_field="coin",
    )
    transaction_time = models.DateTimeField(db_index=True)
    bids = models.JSONField()
    asks = models.JSONField()

    class Meta:
        db_table = "coins_orderbook"
        constraints = [
            models.UniqueConstraint(
                fields=["coin", "transaction_time"], name="orderbook_primary_key"
            )
        ]
        indexes = [
            models.Index(
                fields=["coin", "-transaction_time"], name="orderbook_coin_ts_idx"
            )
        ]

    def __str__(self):
        return f"{self.coin.coin} - {self.transaction_time.isoformat()}"
