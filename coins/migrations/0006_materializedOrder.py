from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "coins",
            "0005_obtimescale",
        ),  # Убедитесь, что это правильная предыдущая миграция
    ]


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "coins",
            "0005_obtimescale",
        ),  # Убедитесь, что это правильная предыдущая миграция
    ]

    operations = [
        # Создание материализованного представления для последнего состояния стакана
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW IF NOT EXISTS current_orderbook AS
            SELECT
                coin_id,
                transaction_time,
                bids,
                asks
            FROM (
                SELECT
                    coin_id,
                    transaction_time,
                    bids,
                    asks,
                    ROW_NUMBER() OVER (PARTITION BY coin_id ORDER BY transaction_time DESC) AS rn
                FROM coins_orderbook
                WHERE transaction_time > NOW() - INTERVAL '1 hour'
            ) subquery
            WHERE rn = 1;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS current_orderbook;",
        ),
        # Добавление индекса
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS current_orderbook_coin_idx
            ON current_orderbook (coin_id);
            """,
            reverse_sql="DROP INDEX IF EXISTS current_orderbook_coin_idx;",
        ),
    ]

    atomic = False  # Отключаем транзакционный блок
