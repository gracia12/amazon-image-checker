from __future__ import annotations

from database import config
from database.postgres_connector import PostgresConnector


class LocalPostgresConnector(PostgresConnector):
    def __init__(self):
        super(LocalPostgresConnector, self).__init__()
        self.kill_all()
        self.create_test_tables()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.kill_all()
        super(LocalPostgresConnector, self).__exit__(exc_type, exc_val, exc_tb)

    def drop_test_tables(self):
        self.run_query(f'DROP TABLE IF EXISTS {config.PRODUCT_READ_HISTORY_TABLE}')
        self.run_query(f'DROP TABLE IF EXISTS {config.PRODUCT_READ_CHANGES_TABLE}')
        self.run_query(f'DROP TABLE IF EXISTS {config.AB_TEST_RUNS_TABLE}')
        self.run_query(f'DROP TABLE IF EXISTS {config.MERCHANTS_TABLE}')

    def create_test_tables(self):
        self.run_query(self.create_product_read_table_query(config.PRODUCT_READ_HISTORY_TABLE))
        self.run_query(self.create_product_read_table_query(config.PRODUCT_READ_CHANGES_TABLE))
        self.run_query(self.create_ab_test_runs_table_query())
        self.run_query(self.create_merchants_table_query())

    def kill_all(self):
        self.drop_test_tables()
