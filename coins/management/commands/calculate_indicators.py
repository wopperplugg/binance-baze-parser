import pandas as pd
from django.core.management.base import BaseCommand
from django.utils import timezone
from coins.models import (
    Kline,
    SentimentIndicator,
    VolatilityLiquidityIndicator,
    TechnicalTrigger,
    Coin,
)
import numpy as np
import time


class Command(BaseCommand):
    help = "Рассчитать и сохранить индикаторы в базе данных"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Количество последних записей kline для обработки (по умолчанию: 100)",
        )
        parser.add_argument(
            "--offset", type=int, default=0, help="Смещение для пакетной обработки"
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        offset = options["offset"]

        self.stdout.write(
            f"Рассчитываются индикаторы для последних {limit} записей kline с смещением {offset}"
        )

        klines = Kline.objects.order_by("-transaction_time")[
            offset : offset + limit
        ].values(
            "transaction_time",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
        )

        if not klines:
            self.stdout.write(self.style.WARNING("Данные kline не найдены"))
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

        start_time = time.time()
        self.calculate_sentiment_indicators(df)
        self.stdout.write(
            self.style.SUCCESS(
                f"Sentiment indicators calculated in {time.time() - start_time:.2f} seconds"
            )
        )

        start_time = time.time()
        self.calculate_volatility_liquidity_indicators(df)
        self.stdout.write(
            self.style.SUCCESS(
                f"Volatility liquidity indicators calculated in {time.time() - start_time:.2f} seconds"
            )
        )

        start_time = time.time()
        self.calculate_technical_triggers(df)
        self.stdout.write(
            self.style.SUCCESS(
                f"Technical triggers calculated in {time.time() - start_time:.2f} seconds"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно рассчитаны и сохранены индикаторы для {len(df)} записей"
            )
        )

    def process_coins(self, df: pd.DataFrame, calculation_function: callable) -> None:
        coins = Coin.objects.all()

        if not coins:
            self.stdout.write(self.style.WARNING("Монеты не найдены"))
            return

        for coin in coins:
            coin_klines = Kline.objects.filter(coin=coin).order_by("-transaction_time")[
                : len(df)
            ]
            if not coin_klines:
                continue

            coin_data = pd.DataFrame(
                list(
                    coin_klines.values(
                        "transaction_time",
                        "open_price",
                        "high_price",
                        "low_price",
                        "close_price",
                        "volume",
                    )
                )
            ).rename(
                columns={
                    "transaction_time": "timestamp",
                    "open_price": "open",
                    "high_price": "high",
                    "low_price": "low",
                    "close_price": "close",
                    "volume": "volume",
                }
            )
            coin_data = coin_data.sort_values("timestamp").reset_index(drop=True)

            calculation_function(coin_data, coin)

    def calculate_sentiment_indicators(self, df):
        """Рассчитывает сентиментальные индикаторы: открытый интерес, ставка финансирования, соотношение длинных/коротких позиций"""

        def calculate_for_coin(coin_data: pd.DataFrame, coin: Coin) -> None:
            if coin_data.empty:
                self.stdout.write(self.style.WARNING(f"Нет данных для монеты {coin}"))
                return
            # Открытый интерес (прокси на основе объема)
            coin_data["open_interest"] = coin_data["volume"].rolling(window=20).mean()
            coin_data["open_interest_change"] = coin_data["open_interest"].pct_change()

            # Ставка финансирования (аппроксимация на основе изменения цены)
            coin_data["price_change_pct"] = coin_data["close"].pct_change()
            coin_data["funding_rate"] = (
                coin_data["price_change_pct"].rolling(window=5).mean() * 0.0001
            )

            # Соотношение длинных/коротких позиций (прокси на основе импульса цены)
            coin_data["returns"] = coin_data["close"].pct_change()
            coin_data["volatility"] = coin_data["returns"].rolling(window=10).std()
            coin_data["price_momentum"] = (
                coin_data["close"] / coin_data["close"].rolling(window=20).mean() - 1
            )

            coin_data["long_short_ratio"] = np.where(
                coin_data["price_momentum"] > 0,
                1
                + np.abs(coin_data["price_momentum"])
                * 0.5,  # Больше длинных позиций, если цена выше средней
                1
                - np.abs(coin_data["price_momentum"])
                * 0.5,  # Больше коротких позиций, если цена ниже средней
            )
            coin_data["long_short_ratio"] = coin_data["long_short_ratio"].clip(
                lower=0.1, upper=10
            )
            
            coin_data = coin_data.replace({np.nan: None, np.inf: None, -np.inf: None})

            # Сохраняем индикаторы в базу данных
            for _, row in coin_data.iterrows():
                SentimentIndicator.objects.update_or_create(
                    coin=coin,
                    transaction_time=row["timestamp"],
                    defaults={
                        "open_interest": row.get("open_interest"),
                        "open_interest_change": row.get("open_interest_change"),
                        "funding_rate": row.get("funding_rate"),
                        "long_short_ratio": row.get("long_short_ratio"),
                        "long_positions": None,  # Эти данные обычно берутся из API биржи
                        "short_positions": None,  # Эти данные обычно берутся из API биржи
                    },
                )

        self.process_coins(df, calculate_for_coin)

    def calculate_volatility_liquidity_indicators(self, df):
        """Рассчитывает индикаторы волатильности и ликвидности: ATR, VWAP, уровни ликвидации"""

        def calculate_for_coin(coin_data: pd.DataFrame, coin: Coin) -> None:
            if coin_data.empty:
                self.stdout.write(self.style.WARNING(f"Нет данных для монеты {coin}"))
                return
            # Рассчитываем True Range для ATR
            coin_data["high_low"] = coin_data["high"] - coin_data["low"]
            coin_data["high_close_prev"] = np.abs(
                coin_data["high"] - coin_data["close"].shift(1)
            )
            coin_data["low_close_prev"] = np.abs(
                coin_data["low"] - coin_data["close"].shift(1)
            )
            coin_data["true_range"] = np.maximum(
                coin_data["high_low"],
                np.maximum(coin_data["high_close_prev"], coin_data["low_close_prev"]),
            )

            # Рассчитываем ATR 14
            coin_data["atr_14"] = coin_data["true_range"].rolling(window=14).mean()

            # Рассчитываем ATR 21
            coin_data["atr_21"] = coin_data["true_range"].rolling(window=21).mean()

            # Рассчитываем VWAP (Volume Weighted Average Price)
            coin_data["typical_price"] = (
                coin_data["high"] + coin_data["low"] + coin_data["close"]
            ) / 3
            coin_data["tpv"] = coin_data["typical_price"] * coin_data["volume"]
            coin_data["vwap"] = (
                coin_data["tpv"].rolling(window=20).sum()
                / coin_data["volume"].rolling(window=20).sum()
            )

            # Добавляем верхнюю и нижнюю границы VWAP
            coin_data["vwap_std"] = coin_data["vwap"].rolling(window=20).std()
            coin_data["vwap_upper_band"] = coin_data["vwap"] + (
                coin_data["vwap_std"] * 2
            )
            coin_data["vwap_lower_band"] = coin_data["vwap"] - (
                coin_data["vwap_std"] * 2
            )

            # Рассчитываем волатильность (стандартное отклонение доходности за 20 периодов)
            coin_data["returns"] = coin_data["close"].pct_change()
            coin_data["volatility"] = coin_data["returns"].rolling(window=20).std()

            # Оцениваем уровни ликвидации на основе волатильности и недавнего движения цены
            coin_data["volatility_pct"] = coin_data["volatility"] * coin_data["close"]
            coin_data["liquidation_resistance"] = coin_data["close"] + (
                coin_data["volatility_pct"] * 2
            )
            coin_data["liquidation_support"] = coin_data["close"] - (
                coin_data["volatility_pct"] * 2
            )

            # Заменяем NaN на None
            coin_data = coin_data.replace({np.nan: None, np.inf: None, -np.inf: None})

            # Сохраняем индикаторы в базу данных
            indicators_to_create = []
            for _, row in coin_data.iterrows():
                VolatilityLiquidityIndicator.objects.update_or_create(
                    coin=coin,
                    transaction_time=row["timestamp"],
                    defaults={
                        "atr_14": row.get("atr_14"),
                        "atr_21": row.get("atr_21"),
                        "vwap": row.get("vwap"),
                        "vwap_high_band": row.get("vwap_upper_band"),
                        "vwap_low_band": row.get("vwap_lower_band"),
                        "liquidation_levels": {
                            "long_levels": [row.get("liquidation_support")],
                            "short_levels": [row.get("liquidation_resistance")],
                        },
                    },
                )

        # Обрабатываем данные для каждой монеты
        self.process_coins(df, calculate_for_coin)

    def calculate_technical_triggers(self, df: pd.DataFrame) -> None:
        """Рассчитывает технические триггеры: EMA, Stochastic RSI, профиль объема"""

        def calculate_for_coin(coin_data: pd.DataFrame, coin: Coin) -> None:
            if coin_data.empty:
                self.stdout.write(self.style.WARNING(f"Нет данных для монеты {coin}"))
                return

            # Рассчитываем EMA
            coin_data["ema_20"] = coin_data["close"].ewm(span=20).mean()
            coin_data["ema_50"] = coin_data["close"].ewm(span=50).mean()
            coin_data["ema_100"] = coin_data["close"].ewm(span=100).mean()
            coin_data["ema_200"] = coin_data["close"].ewm(span=200).mean()

            # Рассчитываем RSI
            rsi_window = 14
            delta = coin_data["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()

            rs = np.where(loss != 0, gain / loss, 0)
            rsi = 100 - (100 / (1 + rs))

            # Рассчитываем Stochastic RSI
            stoch_rsi_window = 14
            rsi_min = pd.Series(rsi).rolling(window=stoch_rsi_window).min()
            rsi_max = pd.Series(rsi).rolling(window=stoch_rsi_window).max()

            stoch_rsi = np.divide(
                rsi - rsi_min,
                rsi_max - rsi_min,
                out=np.full_like(
                    rsi, 50
                ),  # Значение по умолчанию, если делитель равен 0
                where=(rsi_max - rsi_min) != 0,
            )
            stoch_rsi = stoch_rsi * 100

            coin_data["stoch_rsi_k"] = pd.Series(stoch_rsi).rolling(window=3).mean()
            coin_data["stoch_rsi_d"] = coin_data["stoch_rsi_k"].rolling(window=3).mean()

            # Рассчитываем элементы профиля объема
            coin_data["volume_sma"] = coin_data["volume"].rolling(window=20).mean()
            coin_data["volume_ratio"] = np.where(
                coin_data["volume_sma"] != 0,
                coin_data["volume"] / coin_data["volume_sma"],
                1,
            )

            coin_data["typical_price"] = (
                coin_data["high"] + coin_data["low"] + coin_data["close"]
            ) / 3
            coin_data["price_volume"] = coin_data["typical_price"] * coin_data["volume"]
            coin_data["vwap"] = (
                coin_data["price_volume"].rolling(window=20).sum()
                / coin_data["volume"].rolling(window=20).sum()
            )

            # Находим уровни поддержки и сопротивления
            window = 10
            coin_data["local_max"] = (
                coin_data["high"].rolling(window=window, center=True).max()
            )
            coin_data["local_min"] = (
                coin_data["low"].rolling(window=window, center=True).min()
            )

            resistance_levels = (
                coin_data[coin_data["high"] == coin_data["local_max"]]["high"]
                .dropna()
                .tail(5)
                .tolist()
            )
            support_levels = (
                coin_data[coin_data["low"] == coin_data["local_min"]]["low"]
                .dropna()
                .tail(5)
                .tolist()
            )

            coin_data = coin_data.replace({np.nan: None, np.inf: None, -np.inf: None})

            # Сохраняем индикаторы в базу данных
            indicators_to_create = []
            for _, row in coin_data.iterrows():
                indicators_to_create.append(
                    TechnicalTrigger(
                        coin=coin,
                        transaction_time=row["timestamp"],
                        ema_20=row["ema_20"],
                        ema_50=row["ema_50"],
                        ema_100=row["ema_100"],
                        ema_200=row["ema_200"],
                        stoch_rsi_k=row["stoch_rsi_k"],
                        stoch_rsi_d=row["stoch_rsi_d"],
                        volume_profile_nodes={
                            "volume_ratio": row["volume_ratio"],
                            "support_levels": support_levels,
                            "resistance_levels": resistance_levels,
                            "vwap": row["vwap"],
                        },
                    )
                )
            TechnicalTrigger.objects.bulk_create(
                indicators_to_create, ignore_conflicts=True
            )

        self.process_coins(df, calculate_for_coin)
