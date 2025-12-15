from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("coins", "0004_orderbook")]

    operations = [
        migrations.RunSQL(
            sql="create extension if not exists timescaledb cascade;",
            reverse_sql="drop extension if not exists timescaledb cascade;",
        ),
        migrations.RunSQL(
            sql="""
            SELECT create_hypertable(
                'coins_orderbook',
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
                create index if not exists coins_orderbook_symbol_ts_desc_idx
                on coins_orderbook (coin_id, "transaction_time" desc);
                create index if not exists coins_orderbook_transaction_time_brin
                on coins_orderbook using brin ("transaction_time");
                
                alter table coins_orderbook set (
                    timescaledb.compress,
                    timescaledb.compress_segmentby = 'coin_id',
                    timescaledb.compress_orderby = 'transaction_time'
                );
                
                select add_compression_policy('coins_orderbook', interval '3 days');

                select add_retention_policy('coins_orderbook', interval '1 month');
            """,
            reverse_sql="""
                drop index if exists coins_orderbook_symbol_ts_desc_idx;
                drop index if exists coins_orderbook_transaction_time_brin;
                select remove_compression_policy('coins_orderbook');
                alter table coins_orderbok reset (timescaledb.compress, timescaledb.compress_segmentby);
            """,
        ),
    ]
    atomic = False
