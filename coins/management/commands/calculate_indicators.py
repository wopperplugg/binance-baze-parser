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
    help = "Рассчитать и сохранить индикаторы в базе данных"

    def add_arguments(self, parser):
        # Добавляем аргумент командной строки для ограничения количества обрабатываемых записей
        parser.add_argument(
            "--limit",
            type=int,
            default=1000,
            help="Количество последних записей kline для обработки (по умолчанию: 1000)",
        )

    def handle(self, *args, **options):
        # Получаем значение лимита из аргументов командной строки
        limit = options["limit"]
        self.stdout.write(
            f"Рассчитываются индикаторы для последних {limit} записей kline..."
        )

        # Получаем последние записи kline из базы данных
        klines = Kline.objects.order_by("-transaction_time")[:limit].values(
            "transaction_time",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
        )

        if not klines:
            # Если нет данных kline, выводим предупреждение и завершаем выполнение
            self.stdout.write(self.style.WARNING("Данные kline не найдены"))
            return

        # Преобразуем данные в DataFrame Pandas
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

        # Рассчитываем различные типы индикаторов
        self.calculate_sentiment_indicators(df)
        self.calculate_volatility_liquidity_indicators(df)
        self.calculate_technical_triggers(df)

        # Выводим сообщение об успешном завершении
        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно рассчитаны и сохранены индикаторы для {len(df)} записей"
            )
        )

    def calculate_sentiment_indicators(self, df):
        """Рассчитывает сентиментальные индикаторы: открытый интерес, ставка финансирования, соотношение длинных/коротких позиций"""
        # Открытый интерес (прокси на основе объема)
        df["open_interest"] = df["volume"].rolling(window=20).mean()
        df["open_interest_change"] = df["open_interest"].pct_change()

        # Ставка финансирования (аппроксимация на основе изменения цены)
        df["price_change_pct"] = df["close"].pct_change()
        df["funding_rate"] = df["price_change_pct"].rolling(window=5).mean() * 0.0001

        # Соотношение длинных/коротких позиций (прокси на основе импульса цены)
        df["returns"] = df["close"].pct_change()
        df["volatility"] = df["returns"].rolling(window=10).std()
        df["price_momentum"] = df["close"] / df["close"].rolling(window=20).mean() - 1

        df["long_short_ratio"] = np.where(
            df["price_momentum"] > 0,
            1
            + np.abs(df["price_momentum"])
            * 0.5,  # Больше длинных позиций, если цена выше средней
            1
            - np.abs(df["price_momentum"])
            * 0.5,  # Больше коротких позиций, если цена ниже средней
        )
        df["long_short_ratio"] = df["long_short_ratio"].clip(lower=0.1, upper=10)

        from coins.models import Coin

        # Обрабатываем каждую монету отдельно
        coins = Coin.objects.all()
        if not coins:
            self.stdout.write(
                self.style.WARNING(
                    "Монеты не найдены, пропускаем сентиментальные индикаторы"
                )
            )
            return

        for coin in coins:
            # Фильтруем данные kline для конкретной монеты
            coin_klines = Kline.objects.filter(coin=coin).order_by("-transaction_time")[
                : len(df)
            ]
            coin_data = (
                pd.DataFrame(
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
                )
                .rename(
                    columns={
                        "transaction_time": "timestamp",
                        "open_price": "open",
                        "high_price": "high",
                        "low_price": "low",
                        "close_price": "close",
                        "volume": "volume",
                    }
                )
                .sort_values("timestamp")
                .reset_index(drop=True)
            )

            if len(coin_data) == 0:
                continue

            # Пересчитываем индикаторы для этой монеты
            coin_data["open_interest"] = coin_data["volume"].rolling(window=20).mean()
            coin_data["open_interest_change"] = coin_data["open_interest"].pct_change()

            coin_data["price_change_pct"] = coin_data["close"].pct_change()
            coin_data["funding_rate"] = (
                coin_data["price_change_pct"].rolling(window=5).mean() * 0.0001
            )

            coin_data["returns"] = coin_data["close"].pct_change()
            coin_data["volatility"] = coin_data["returns"].rolling(window=10).std()
            coin_data["price_momentum"] = (
                coin_data["close"] / coin_data["close"].rolling(window=20).mean() - 1
            )

            coin_data["long_short_ratio"] = np.where(
                coin_data["price_momentum"] > 0,
                1 + np.abs(coin_data["price_momentum"]) * 0.5,
                1 - np.abs(coin_data["price_momentum"]) * 0.5,
            )
            coin_data["long_short_ratio"] = coin_data["long_short_ratio"].clip(
                lower=0.1, upper=10
            )

            # Сохраняем индикаторы в базу данных
            for _, row in coin_data.iterrows():
                SentimentIndicator.objects.update_or_create(
                    coin=coin,
                    transaction_time=row["timestamp"],
                    defaults={
                        "open_interest": row["open_interest"],
                        "open_interest_change": row["open_interest_change"],
                        "funding_rate": row["funding_rate"],
                        "long_short_ratio": row["long_short_ratio"],
                        "long_positions": None,  # Эти данные обычно берутся из API биржи
                        "short_positions": None,  # Эти данные обычно берутся из API биржи
                    },
                )

    def calculate_volatility_liquidity_indicators(self, df):
        """Рассчитывает индикаторы волатильности и ликвидности: ATR, VWAP, уровни ликвидации"""
        # Рассчитываем True Range для ATR
        df["high_low"] = df["high"] - df["low"]
        df["high_close_prev"] = np.abs(df["high"] - df["close"].shift(1))
        df["low_close_prev"] = np.abs(df["low"] - df["close"].shift(1))
        df["true_range"] = np.maximum(
            df["high_low"], np.maximum(df["high_close_prev"], df["low_close_prev"])
        )
        df["atr_14"] = df["true_range"].rolling(window=14).mean()

        # Рассчитываем VWAP (Volume Weighted Average Price)
        df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
        df["tpv"] = df["typical_price"] * df["volume"]
        df["vwap"] = (
            df["tpv"].rolling(window=20).sum() / df["volume"].rolling(window=20).sum()
        )

        # Добавляем верхнюю и нижнюю границы VWAP
        df["vwap_std"] = df["vwap"].rolling(window=20).std()
        df["vwap_upper_band"] = df["vwap"] + (df["vwap_std"] * 2)
        df["vwap_lower_band"] = df["vwap"] - (df["vwap_std"] * 2)

        # Рассчитываем волатильность (стандартное отклонение доходности за 20 периодов)
        df["returns"] = df["close"].pct_change()
        df["volatility"] = df["returns"].rolling(window=20).std()

        # Оцениваем уровни ликвидации на основе волатильности и недавнего движения цены
        df["volatility_pct"] = df["volatility"] * df["close"]
        df["liquidation_resistance"] = df["close"] + (df["volatility_pct"] * 2)
        df["liquidation_support"] = df["close"] - (df["volatility_pct"] * 2)

        from coins.models import Coin

        # Обрабатываем каждую монету отдельно
        coins = Coin.objects.all()
        if not coins:
            self.stdout.write(
                self.style.WARNING(
                    "Монеты не найдены, пропускаем индикаторы волатильности"
                )
            )
            return

        for coin in coins:
            # Фильтруем данные kline для конкретной монеты
            coin_klines = Kline.objects.filter(coin=coin).order_by("-transaction_time")[
                : len(df)
            ]
            coin_data = (
                pd.DataFrame(
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
                )
                .rename(
                    columns={
                        "transaction_time": "timestamp",
                        "open_price": "open",
                        "high_price": "high",
                        "low_price": "low",
                        "close_price": "close",
                        "volume": "volume",
                    }
                )
                .sort_values("timestamp")
                .reset_index(drop=True)
            )

            if len(coin_data) == 0:
                continue

            # Пересчитываем индикаторы для этой монеты
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
            coin_data["atr_14"] = coin_data["true_range"].rolling(window=14).mean()

            coin_data["typical_price"] = (
                coin_data["high"] + coin_data["low"] + coin_data["close"]
            ) / 3
            coin_data["tpv"] = coin_data["typical_price"] * coin_data["volume"]
            coin_data["vwap"] = (
                coin_data["tpv"].rolling(window=20).sum()
                / coin_data["volume"].rolling(window=20).sum()
            )

            coin_data["vwap_std"] = coin_data["vwap"].rolling(window=20).std()
            coin_data["vwap_upper_band"] = coin_data["vwap"] + (
                coin_data["vwap_std"] * 2
            )
            coin_data["vwap_lower_band"] = coin_data["vwap"] - (
                coin_data["vwap_std"] * 2
            )

            coin_data["returns"] = coin_data["close"].pct_change()
            coin_data["volatility"] = coin_data["returns"].rolling(window=20).std()
            coin_data["volatility_pct"] = coin_data["volatility"] * coin_data["close"]
            coin_data["liquidation_resistance"] = coin_data["close"] + (
                coin_data["volatility_pct"] * 2
            )
            coin_data["liquidation_support"] = coin_data["close"] - (
                coin_data["volatility_pct"] * 2
            )

            # Сохраняем индикаторы в базу данных
            for _, row in coin_data.iterrows():
                VolatilityLiquidityIndicator.objects.update_or_create(
                    coin=coin,
                    transaction_time=row["timestamp"],
                    defaults={
                        "atr_14": row["atr_14"],
                        "atr_21": None,  # Можно рассчитать с окном 21 периода, если нужно
                        "vwap": row["vwap"],
                        "vwap_high_band": row["vwap_upper_band"],
                        "vwap_low_band": row["vwap_lower_band"],
                        "liquidation_levels": {
                            "long_levels": [row["liquidation_support"]],
                            "short_levels": [row["liquidation_resistance"]],
                        },
                    },
                )

    def calculate_technical_triggers(self, df):
        """Рассчитывает технические триггеры: EMA, Stochastic RSI, профиль объема"""
        # Рассчитываем экспоненциальные скользящие средние (EMA)
        df["ema_20"] = df["close"].ewm(span=20).mean()
        df["ema_50"] = df["close"].ewm(span=50).mean()
        df["ema_100"] = df["close"].ewm(span=100).mean()
        df["ema_200"] = df["close"].ewm(span=200).mean()

        # Рассчитываем RSI (Relative Strength Index)
        rsi_window = 14
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()

        rs = np.where(loss != 0, gain / loss, 0)
        rsi = 100 - (100 / (1 + rs))

        # Рассчитываем Stochastic RSI
        stoch_rsi_window = 14
        rsi_min = pd.Series(rsi).rolling(window=stoch_rsi_window).min()
        rsi_max = pd.Series(rsi).rolling(window=stoch_rsi_window).max()

        stoch_rsi = np.where(
            rsi_max - rsi_min != 0, (rsi - rsi_min) / (rsi_max - rsi_min) * 100, 50
        )

        df["stoch_rsi_k"] = pd.Series(stoch_rsi).rolling(window=3).mean()
        df["stoch_rsi_d"] = df["stoch_rsi_k"].rolling(window=3).mean()

        # Рассчитываем элементы профиля объема
        df["volume_sma"] = df["volume"].rolling(window=20).mean()
        df["volume_ratio"] = np.where(
            df["volume_sma"] != 0, df["volume"] / df["volume_sma"], 1
        )

        df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
        df["price_volume"] = df["typical_price"] * df["volume"]
        df["vwap"] = (
            df["price_volume"].rolling(window=20).sum()
            / df["volume"].rolling(window=20).sum()
        )

        # Находим уровни поддержки и сопротивления на основе локальных минимумов/максимумов
        window = 5
        df["local_max"] = df["high"].rolling(window=window, center=True).max()
        df["local_min"] = df["low"].rolling(window=window, center=True).min()

        resistance_levels = (
            df[df["high"] == df["local_max"]]["high"].dropna().tail(5).tolist()
        )
        support_levels = (
            df[df["low"] == df["local_min"]]["low"].dropna().tail(5).tolist()
        )

        from coins.models import Coin

        # Обрабатываем каждую монету отдельно
        coins = Coin.objects.all()
        if not coins:
            self.stdout.write(
                self.style.WARNING("Монеты не найдены, пропускаем технические триггеры")
            )
            return

        for coin in coins:
            # Фильтруем данные kline для конкретной монеты
            coin_klines = Kline.objects.filter(coin=coin).order_by("-transaction_time")[
                : len(df)
            ]
            coin_data = (
                pd.DataFrame(
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
                )
                .rename(
                    columns={
                        "transaction_time": "timestamp",
                        "open_price": "open",
                        "high_price": "high",
                        "low_price": "low",
                        "close_price": "close",
                        "volume": "volume",
                    }
                )
                .sort_values("timestamp")
                .reset_index(drop=True)
            )

            if len(coin_data) == 0:
                continue

            # Пересчитываем индикаторы для этой монеты
            coin_data["ema_20"] = coin_data["close"].ewm(span=20).mean()
            coin_data["ema_50"] = coin_data["close"].ewm(span=50).mean()
            coin_data["ema_100"] = coin_data["close"].ewm(span=100).mean()
            coin_data["ema_200"] = coin_data["close"].ewm(span=200).mean()

            delta = coin_data["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()
            rs = np.where(loss != 0, gain / loss, 0)
            rsi = 100 - (100 / (1 + rs))

            rsi_series = pd.Series(rsi)
            rsi_min = rsi_series.rolling(window=stoch_rsi_window).min()
            rsi_max = rsi_series.rolling(window=stoch_rsi_window).max()
            stoch_rsi = np.where(
                rsi_max - rsi_min != 0, (rsi - rsi_min) / (rsi_max - rsi_min) * 100, 50
            )

            coin_data["stoch_rsi_k"] = pd.Series(stoch_rsi).rolling(window=3).mean()
            coin_data["stoch_rsi_d"] = coin_data["stoch_rsi_k"].rolling(window=3).mean()

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

            window = 5
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

            # Сохраняем индикаторы в базу данных
            for _, row in coin_data.iterrows():
                TechnicalTrigger.objects.update_or_create(
                    coin=coin,
                    transaction_time=row["timestamp"],
                    defaults={
                        "ema_20": row["ema_20"],
                        "ema_50": row["ema_50"],
                        "ema_100": row["ema_100"],
                        "ema_200": row["ema_200"],
                        "stoch_rsi_k": row["stoch_rsi_k"],
                        "stoch_rsi_d": row["stoch_rsi_d"],
                        "volume_profile_nodes": {
                            "volume_ratio": row["volume_ratio"],
                            "support_levels": support_levels,
                            "resistance_levels": resistance_levels,
                            "vwap": row["vwap"],
                        },
                    },
                )
