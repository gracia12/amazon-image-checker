from __future__ import annotations

import logging
import os

import psycopg2
from psycopg2.extras import RealDictCursor

from database import config
from database.base_connector import BaseConnector
from database.data_model import SQLQuery


class PostgresConnector(BaseConnector):
    def create_new_connection(self) -> object:
        pg_connect = psycopg2.connect(os.environ['DATABASE_URL'])
        pg_connect.set_session(autocommit=True)
        return pg_connect

    def init_cursor(self):
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def is_connected(self) -> bool:
        return self.connection is not None and not self.connection.closed

    def handle_error(self, error: psycopg2.Error, query: SQLQuery):
        logging.error(f'ERROR {error.pgcode} {error}: {query}')

    def create_product_read_table_query(self, table_name: str) -> str:
        return f'CREATE TABLE IF NOT EXISTS {table_name} ' \
               f'({config.ASIN_FIELD} TEXT, ' \
               f'{config.READ_TIME_FIELD} TIMESTAMP, ' \
               f'{config.IMAGE_VARIATIONS_FIELD} JSON, ' \
               f'{config.LISTING_PRICE_FIELD} FLOAT, ' \
               f'{config.IS_ACTIVE_FIELD} BOOLEAN, ' \
               f'{config.MERCHANT_FIELD} TEXT, ' \
               f'PRIMARY KEY ({config.ASIN_FIELD}, {config.READ_TIME_FIELD}))'

    def create_ab_test_runs_table_query(self) -> str:
        return f'CREATE TABLE IF NOT EXISTS {config.AB_TEST_RUNS_TABLE} ' \
               f'({config.RUN_ID_FIELD} SERIAL PRIMARY KEY NOT NULL, ' \
               f'{config.AB_TEST_ID_FIELD} INT, ' \
               f'{config.RUN_TIME_FIELD} TIMESTAMP, ' \
               f'{config.FEED_ID_FIELD} BIGINT, ' \
               f'{config.VARIATION_FIELD} TEXT, ' \
               f'{config.MERCHANT_FIELD} TEXT)'

    def create_merchants_table_query(self) -> str:
        return f'CREATE TABLE IF NOT EXISTS {config.MERCHANTS_TABLE} ' \
               f'({config.MERCHANT_ID_FIELD} SERIAL PRIMARY KEY NOT NULL, ' \
               f'{config.LWA_CLIENT_SECRET_FIELD} TEXT, ' \
               f'{config.LWA_APP_ID_FIELD} TEXT, ' \
               f'{config.SP_API_SECRET_KEY_FIELD} TEXT, ' \
               f'{config.SP_API_ROLE_ARN_FIELD} TEXT, ' \
               f'{config.SP_API_REFRESH_TOKEN_FIELD} TEXT, ' \
               f'{config.SP_API_ACCESS_KEY_FIELD} TEXT, ' \
               f'{config.MERCHANT_FIELD} TEXT)'
