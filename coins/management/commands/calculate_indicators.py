import pandas as pd
from django.core.management.base import BaseCommand
from django.utils import timezone
from coins.models import (
    Kline,
    SentimentIndicator,
    VolatilityLiquidityIndicator,
    TechnicalTrigger,
)
import numpy as np


class Command(BaseCommand):
    help = "Calculate and store indicators in the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=1000,
            help="Number of recent kline records to process (default: 1000)",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        self.stdout.write(f"Calculating indicators for last {limit} kline records...")

        klines = Kline.objects.order_by("-transaction_time")[:limit].values(
            "transaction_time",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
        )

        if not klines:
            self.stdout.write(self.style.WARNING("No kline data found"))
            return

        df = pd.DataFrame(list(klines))
        df = df.rename(
            columns={
                "transaction_time": "timestamp",
                "open_price": "open",
                "high_price": "high",
                "low_price": "low",
                "close_price": "close",
                "volume": "volume",
            }
        )
        df = df.sort_values("timestamp").reset_index(drop=True)

        self.calculate_sentiment_indicators(df)
        self.calculate_volatility_liquidity_indicators(df)
        self.calculate_technical_triggers(df)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully calculated and stored indicators for {len(df)} records"
            )
        )

    def calculate_sentiment_indicators(self, df):
        """Calculate sentiment indicators: open interest, funding rate, long/short ratio"""
        df["open_interest"] = df["volume"].rolling(window=20).mean()

        df["price_change"] = df["close"].pct_change()
        df["funding_rate"] = df["price_change"].rolling(window=10).std() * 0.01

        df["long_short_ratio"] = np.where(
            df["close"] > df["open"],
            1 + df["volume"] / df["volume"].rolling(window=20).mean(),
            1 - df["volume"] / df["volume"].rolling(window=20).mean(),
        )
        df["long_short_ratio"] = df["long_short_ratio"].clip(lower=0.1)

        from coins.models import Coin

        coin = Coin.objects.first()
        if not coin:
            self.stdout.write(
                self.style.WARNING("No coin found, skipping sentiment indicators")
            )
            return

        for _, row in df.iterrows():
            SentimentIndicator.objects.update_or_create(
                coin=coin,
                transaction_time=row["timestamp"],
                defaults={
                    "open_interest": row["open_interest"],
                    "funding_rate": row["funding_rate"],
                    "long_short_ratio": row["long_short_ratio"],
                },
            )

    def calculate_volatility_liquidity_indicators(self, df):
        """Calculate volatility and liquidity indicators: ATR, VWAP, liquidation levels"""
        df["high_low"] = df["high"] - df["low"]
        df["high_close"] = np.abs(df["high"] - df["close"].shift())
        df["low_close"] = np.abs(df["low"] - df["close"].shift())
        df["true_range"] = df[["high_low", "high_close", "low_close"]].max(axis=1)
        df["atr"] = df["true_range"].rolling(window=14).mean()

        df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
        df["vwap"] = (df["typical_price"] * df["volume"]).cumsum() / df[
            "volume"
        ].cumsum()

        df["volatility"] = df["close"].rolling(window=20).std()
        df["liquidation_resistance"] = df["close"] + (df["volatility"] * 0.5)
        df["liquidation_support"] = df["close"] - (df["volatility"] * 0.5)

        from coins.models import Coin

        coin = Coin.objects.first()
        if not coin:
            self.stdout.write(
                self.style.WARNING("No coin found, skipping volatility indicators")
            )
            return

        for _, row in df.iterrows():
            VolatilityLiquidityIndicator.objects.update_or_create(
                coin=coin,
                transaction_time=row["timestamp"],
                defaults={
                    "atr_14": row["atr"],
                    "vwap": row["vwap"],
                    "liquidation_levels": {
                        "resistance": row["liquidation_resistance"],
                        "support": row["liquidation_support"],
                    },
                },
            )

    def calculate_technical_triggers(self, df):
        """Calculate technical triggers: EMA, Stochastic RSI, Volume Profile"""
        df["ema_20"] = df["close"].ewm(span=20).mean()
        df["ema_50"] = df["close"].ewm(span=50).mean()

        rsi_window = 14
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        stoch_rsi_k = 3
        df["rsi_min"] = rsi.rolling(window=stoch_rsi_k).min()
        df["rsi_max"] = rsi.rolling(window=stoch_rsi_k).max()
        df["stoch_rsi_k"] = (rsi - df["rsi_min"]) / (df["rsi_max"] - df["rsi_min"])
        df["stoch_rsi_k"] = df["stoch_rsi_k"].rolling(window=3).mean()
        df["stoch_rsi_d"] = df["stoch_rsi_k"].rolling(window=3).mean()

        # Calculate volume profile elements
        df["volume_sma"] = df["volume"].rolling(window=20).mean()
        df["volume_ratio"] = df["volume"] / df["volume_sma"]

        from coins.models import Coin

        coin = Coin.objects.first()
        if not coin:
            self.stdout.write(
                self.style.WARNING("No coin found, skipping technical triggers")
            )
            return

        for _, row in df.iterrows():
            TechnicalTrigger.objects.update_or_create(
                coin=coin,
                transaction_time=row["timestamp"],
                defaults={
                    "ema_20": row["ema_20"],
                    "ema_50": row["ema_50"],
                    "stoch_rsi_k": row["stoch_rsi_k"],
                    "stoch_rsi_d": row["stoch_rsi_d"],
                    "volume_profile_nodes": {"volume_ratio": row["volume_ratio"]},
                },
            )
