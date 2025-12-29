# your_app/migrations/000X_setup_timescale_for_new_indicators.py

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "coins",
            "0008_remove_sentimentindicator_sentiment_indicator_primary_key_and_more",
        ),  # Убедитесь, что это правильный номер
    ]

    operations = [
        # 1. Убедимся, что TimescaleDB включён
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;",
            reverse_sql="DROP EXTENSION IF EXISTS timescaledb CASCADE;",  # Внимание: это может повредить другие гипертаблицы!
        ),
        # 2. Преобразование таблиц в гипертаблицы
        migrations.RunSQL(
            sql="""
            SELECT create_hypertable(
                'sentiment_indicators',
                'transaction_time',
                partitioning_column => 'coin_id',
                number_partitions => 32,
                chunk_time_interval => INTERVAL '1 day',
                if_not_exists => TRUE
            );
            """,
            reverse_sql="-- no-op",
        ),
        migrations.RunSQL(
            sql="""
            SELECT create_hypertable(
                'volatility_liquidity_indicators',
                'transaction_time',
                partitioning_column => 'coin_id',
                number_partitions => 32,
                chunk_time_interval => INTERVAL '1 day',
                if_not_exists => TRUE
            );
            """,
            reverse_sql="-- no-op",
        ),
        migrations.RunSQL(
            sql="""
            SELECT create_hypertable(
                'technical_triggers',
                'transaction_time',
                partitioning_column => 'coin_id',
                number_partitions => 32,
                chunk_time_interval => INTERVAL '1 day',
                if_not_exists => TRUE
            );
            """,
            reverse_sql="-- no-op",
        ),
        # 3. Индексы и сжатие для sentiment_indicators
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS sentiment_indicators_coin_ts_desc_idx
                ON sentiment_indicators (coin_id, "transaction_time" DESC);
                CREATE INDEX IF NOT EXISTS sentiment_indicators_transaction_time_brin
                ON sentiment_indicators USING BRIN ("transaction_time");

                ALTER TABLE sentiment_indicators SET (
                    timescaledb.compress,
                    timescaledb.compress_segmentby = 'coin_id',
                    timescaledb.compress_orderby = 'transaction_time'
                );

                SELECT add_compression_policy('sentiment_indicators', INTERVAL '3 days');
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS sentiment_indicators_coin_ts_desc_idx;
                DROP INDEX IF EXISTS sentiment_indicators_transaction_time_brin;
                SELECT remove_compression_policy('sentiment_indicators');
                ALTER TABLE sentiment_indicators RESET (timescaledb.compress, timescaledb.compress_segmentby);
            """,
        ),
        # 4. Индексы и сжатие для volatility_liquidity_indicators
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS volat_liquidity_indicators_coin_ts_desc_idx
                ON volatility_liquidity_indicators (coin_id, "transaction_time" DESC);
                CREATE INDEX IF NOT EXISTS volat_liquidity_indicators_transaction_time_brin
                ON volatility_liquidity_indicators USING BRIN ("transaction_time");

                ALTER TABLE volatility_liquidity_indicators SET (
                    timescaledb.compress,
                    timescaledb.compress_segmentby = 'coin_id',
                    timescaledb.compress_orderby = 'transaction_time'
                );

                SELECT add_compression_policy('volatility_liquidity_indicators', INTERVAL '3 days');
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS volat_liquidity_indicators_coin_ts_desc_idx;
                DROP INDEX IF EXISTS volat_liquidity_indicators_transaction_time_brin;
                SELECT remove_compression_policy('volatility_liquidity_indicators');
                ALTER TABLE volatility_liquidity_indicators RESET (timescaledb.compress, timescaledb.compress_segmentby);
            """,
        ),
        # 5. Индексы и сжатие для technical_triggers
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS tech_triggers_coin_ts_desc_idx
                ON technical_triggers (coin_id, "transaction_time" DESC);
                CREATE INDEX IF NOT EXISTS tech_triggers_transaction_time_brin
                ON technical_triggers USING BRIN ("transaction_time");

                ALTER TABLE technical_triggers SET (
                    timescaledb.compress,
                    timescaledb.compress_segmentby = 'coin_id',
                    timescaledb.compress_orderby = 'transaction_time'
                );

                SELECT add_compression_policy('technical_triggers', INTERVAL '3 days');
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS tech_triggers_coin_ts_desc_idx;
                DROP INDEX IF EXISTS tech_triggers_transaction_time_brin;
                SELECT remove_compression_policy('technical_triggers');
                ALTER TABLE technical_triggers RESET (timescaledb.compress, timescaledb.compress_segmentby);
            """,
        ),
    ]

    # Устанавливаем atomic в False, так как TimescaleDB несовместим с транзакциями
    atomic = False
