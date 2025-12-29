from django.db import models
from django.utils import timezone
from django.db.models import JSONField
import decimal


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


class SentimentIndicator(models.Model):
    """
    индикаторы рыночных настроений (Open Interest, Fuding Rate, Long/Short Ratio)
    """

    pk = models.CompositePrimaryKey("coin_id", "transaction_time")
    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="sentiment_indicator",
        db_index=True,
        to_field="coin",
    )
    transaction_time = models.DateTimeField(db_index=True)

    # Открытый интерес
    open_interest = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    open_interest_change = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )

    # Ставка финансирования
    funding_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    next_funding_time = models.DateTimeField(null=True)

    # соотношения Long/Short
    long_short_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    long_positions = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    short_positions = models.DecimalField(max_digits=20, decimal_places=8, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "sentiment_indicators"
        constraints = [
            models.UniqueConstraint(
                fields=["coin", "transaction_time"],
                name="sentim_primary_key",
            )
        ]
        indexes = [
            models.Index(
                fields=["coin", "-transaction_time"],
                name="sentim_coin_ts_idx",
            )
        ]

    def __str__(self):
        return f"Sentiment {self.coin.coin} @ {self.transaction_time.isoformat()}"


class VolatilityLiquidityIndicator(models.Model):
    """
    индикаторы волатильности и ликвидности (ATR, VWAP, Liquidation Levels)
    """

    pk = models.CompositePrimaryKey("coin_id", "transaction_time")
    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="volatility_liquidity_indicator",
        db_index=True,
        to_field="coin",
    )
    transaction_time = models.DateTimeField(db_index=True)

    # ATR (Average True Range)
    atr_14 = models.DecimalField(max_digits=15, decimal_places=8, null=True)
    atr_21 = models.DecimalField(max_digits=15, decimal_places=8, null=True)

    # VWAP (Volume Weighted Average Price) - рассчитывается на основе Kline
    vwap = models.DecimalField(max_digits=15, decimal_places=8, null=True)
    vwap_high_band = models.DecimalField(
        max_digits=15, decimal_places=8, null=True
    )  # верхняя граница
    vwap_low_band = models.DecimalField(
        max_digits=15, decimal_places=8, null=True
    )  # нижняя граница

    # Ликвидационные уровни (хранятся как JSON для гибкости)
    liquidation_levels = JSONField(
        null=True, help_text="Словарь с ключами 'long_levels', 'short_levels'"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "volatility_liquidity_indicators"
        constraints = [
            models.UniqueConstraint(
                fields=["coin", "transaction_time"],
                name="vol_indicator_primary_key",
            )
        ]
        indexes = [
            models.Index(
                fields=["coin", "-transaction_time"],
                name="vol_indicator_coin_ts_idx",
            )
        ]

    def __str__(self):
        return f"Volatility/Liquidity {self.coin.coin} @ {self.transaction_time.isoformat()}"


class TechnicalTrigger(models.Model):
    """
    технические триггеры (EMA, Stochastic RSI, Volume Profile)
    """

    pk = models.CompositePrimaryKey("coin_id", "transaction_time")
    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="technical_trigger",
        db_index=True,
        to_field="coin",
    )
    transaction_time = models.DateTimeField(db_index=True)

    # EMA
    ema_20 = models.DecimalField(max_digits=15, decimal_places=8, null=True)
    ema_50 = models.DecimalField(max_digits=15, decimal_places=8, null=True)
    ema_100 = models.DecimalField(max_digits=15, decimal_places=8, null=True)
    ema_200 = models.DecimalField(max_digits=15, decimal_places=8, null=True)

    # Stochastic RSI
    stoch_rsi_k = models.DecimalField(max_digits=6, decimal_places=4, null=True)  # %K
    stoch_rsi_d = models.DecimalField(max_digits=6, decimal_places=4, null=True)  # %D

    # Volume Profile (упрощённо - ключевые уровни)
    volume_profile_nodes = JSONField(
        null=True, help_text="Словарь с ценовыми уровнями и объемами"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "technical_triggers"
        constraints = [
            models.UniqueConstraint(
                fields=["coin", "transaction_time"],
                name="tech_primary_key",
            )
        ]
        indexes = [
            models.Index(
                fields=["coin", "-transaction_time"],
                name="tech_coin_ts_idx",
            )
        ]

    def __str__(self):
        return (
            f"Technical Trigger {self.coin.coin} @ {self.transaction_time.isoformat()}"
        )
