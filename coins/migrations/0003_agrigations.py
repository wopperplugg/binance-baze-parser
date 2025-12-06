from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "coins",
            "0002_timescale",
        ),  # Убедитесь, что это правильная предыдущая миграция
    ]

    operations = [
        # coins_kline_5m
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW IF NOT EXISTS coins_kline_5m
            WITH (timescaledb.continuous) AS
            SELECT
                coin_id AS coin_id,
                time_bucket('5 minutes', transaction_time) AS bucket,
                first(open_price, transaction_time) AS open_price,
                max(high_price) AS high_price,
                min(low_price) AS low_price,
                last(close_price, transaction_time) AS close_price,
                sum(volume) AS volume
            FROM coins_kline
            GROUP BY coin_id, bucket;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS coins_kline_5m;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS coins_kline_5m_coin_bucket_idx
            ON coins_kline_5m (coin_id, bucket DESC);
            """,
            reverse_sql="DROP INDEX IF EXISTS coins_kline_5m_coin_bucket_idx;",
        ),
        migrations.RunSQL(
            sql="""
            SELECT add_continuous_aggregate_policy('coins_kline_5m',
                start_offset => INTERVAL '7 days',
                end_offset => INTERVAL '0 minutes',
                schedule_interval => INTERVAL '1 minute');
            """,
            reverse_sql="""
            SELECT remove_continuous_aggregate_policy('coins_kline_5m');
            """,
        ),
        # coins_kline_15m
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW IF NOT EXISTS coins_kline_15m
            WITH (timescaledb.continuous) AS
            SELECT
                coin_id AS coin_id,
                time_bucket('15 minutes', transaction_time) AS bucket,
                first(open_price, transaction_time) AS open_price,
                max(high_price) AS high_price,
                min(low_price) AS low_price,
                last(close_price, transaction_time) AS close_price,
                sum(volume) AS volume
            FROM coins_kline
            GROUP BY coin_id, bucket;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS coins_kline_15m;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS coins_kline_15m_coin_bucket_idx
            ON coins_kline_15m (coin_id, bucket DESC);
            """,
            reverse_sql="DROP INDEX IF EXISTS coins_kline_15m_coin_bucket_idx;",
        ),
        migrations.RunSQL(
            sql="""
            SELECT add_continuous_aggregate_policy('coins_kline_15m',
                start_offset => INTERVAL '14 days',
                end_offset => INTERVAL '0 minutes',
                schedule_interval => INTERVAL '5 minutes');
            """,
            reverse_sql="""
            SELECT remove_continuous_aggregate_policy('coins_kline_15m');
            """,
        ),
        # coins_kline_1h
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW IF NOT EXISTS coins_kline_1h
            WITH (timescaledb.continuous) AS
            SELECT
                coin_id AS coin_id,
                time_bucket('1 hour', transaction_time) AS bucket,
                first(open_price, transaction_time) AS open_price,
                max(high_price) AS high_price,
                min(low_price) AS low_price,
                last(close_price, transaction_time) AS close_price,
                sum(volume) AS volume
            FROM coins_kline
            GROUP BY coin_id, bucket;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS coins_kline_1h;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS coins_kline_1h_coin_bucket_idx
            ON coins_kline_1h (coin_id, bucket DESC);
            """,
            reverse_sql="DROP INDEX IF EXISTS coins_kline_1h_coin_bucket_idx;",
        ),
        migrations.RunSQL(
            sql="""
            SELECT add_continuous_aggregate_policy('coins_kline_1h',
                start_offset => INTERVAL '30 days',
                end_offset => INTERVAL '0 minutes',
                schedule_interval => INTERVAL '15 minutes');
            """,
            reverse_sql="""
            SELECT remove_continuous_aggregate_policy('coins_kline_1h');
            """,
        ),
        # coins_kline_4h
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW IF NOT EXISTS coins_kline_4h
            WITH (timescaledb.continuous) AS
            SELECT
                coin_id AS coin_id,
                time_bucket('4 hours', transaction_time) AS bucket,
                first(open_price, transaction_time) AS open_price,
                max(high_price) AS high_price,
                min(low_price) AS low_price,
                last(close_price, transaction_time) AS close_price,
                sum(volume) AS volume
            FROM coins_kline
            GROUP BY coin_id, bucket;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS coins_kline_4h;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS coins_kline_4h_coin_bucket_idx
            ON coins_kline_4h (coin_id, bucket DESC);
            """,
            reverse_sql="DROP INDEX IF EXISTS coins_kline_4h_coin_bucket_idx;",
        ),
        migrations.RunSQL(
            sql="""
            SELECT add_continuous_aggregate_policy('coins_kline_4h',
                start_offset => INTERVAL '90 days',
                end_offset => INTERVAL '0 minutes',
                schedule_interval => INTERVAL '1 hour');
            """,
            reverse_sql="""
            SELECT remove_continuous_aggregate_policy('coins_kline_4h');
            """,
        ),
        # coins_kline_1d
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW IF NOT EXISTS coins_kline_1d
            WITH (timescaledb.continuous) AS
            SELECT
                coin_id AS coin_id,
                time_bucket('1 day', transaction_time) AS bucket,
                first(open_price, transaction_time) AS open_price,
                max(high_price) AS high_price,
                min(low_price) AS low_price,
                last(close_price, transaction_time) AS close_price,
                sum(volume) AS volume
            FROM coins_kline
            GROUP BY coin_id, bucket;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS coins_kline_1d;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS coins_kline_1d_coin_bucket_idx
            ON coins_kline_1d (coin_id, bucket DESC);
            """,
            reverse_sql="DROP INDEX IF EXISTS coins_kline_1d_coin_bucket_idx;",
        ),
        migrations.RunSQL(
            sql="""
            SELECT add_continuous_aggregate_policy('coins_kline_1d',
                start_offset => INTERVAL '180 days',
                end_offset => INTERVAL '0 minutes',
                schedule_interval => INTERVAL '6 hours');
            """,
            reverse_sql="""
            SELECT remove_continuous_aggregate_policy('coins_kline_1d');
            """,
        ),
        # coins_kline_1w
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW IF NOT EXISTS coins_kline_1w
            WITH (timescaledb.continuous) AS
            SELECT
                coin_id AS coin_id,
                time_bucket('1 week', transaction_time) AS bucket,
                first(open_price, transaction_time) AS open_price,
                max(high_price) AS high_price,
                min(low_price) AS low_price,
                last(close_price, transaction_time) AS close_price,
                sum(volume) AS volume
            FROM coins_kline
            GROUP BY coin_id, bucket;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS coins_kline_1w;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS coins_kline_1w_coin_bucket_idx
            ON coins_kline_1w (coin_id, bucket DESC);
            """,
            reverse_sql="DROP INDEX IF EXISTS coins_kline_1w_coin_bucket_idx;",
        ),
        migrations.RunSQL(
            sql="""
            SELECT add_continuous_aggregate_policy('coins_kline_1w',
                start_offset => INTERVAL '365 days',
                end_offset => INTERVAL '0 minutes',
                schedule_interval => INTERVAL '1 day');
            """,
            reverse_sql="""
            SELECT remove_continuous_aggregate_policy('coins_kline_1w');
            """,
        ),
    ]

    atomic = False  # Отключаем транзакционный блок
