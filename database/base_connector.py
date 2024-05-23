from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any

from database.data_model import SQLQuery


class BaseConnector:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def run_query(self, query: SQLQuery, verbose: bool = True) -> list[Any]:
        results = []
        try:
            self.connect()
            if verbose:
                logging.debug(f'running query: {query}')
            self.cursor.execute(query)
            self.connection.commit()
            if self.should_fetch(query):
                results = self.cursor.fetchall()
        except Exception as error:
            self.handle_error(error, query)
            raise error
        finally:
            if self.is_connected():
                self.close_connection()
            if verbose:
                logging.info(f'got results {results} for {query}')
            return results

    def should_fetch(self, query: SQLQuery) -> bool:
        return query.lower().startswith('select') and self.cursor.rowcount > 0

    @abstractmethod
    def handle_error(self, error: Exception, query: SQLQuery):
        pass

    @abstractmethod
    def create_new_connection(self) -> object:
        pass

    @abstractmethod
    def init_cursor(self):
        pass

    def connect(self):
        if not self.is_connected():
            self.connection = self.create_new_connection()
        self.init_cursor()

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    @abstractmethod
    def create_merchants_table_query(self) -> str:
        pass

    @abstractmethod
    def create_ab_test_runs_table_query(self) -> str:
        pass

    @abstractmethod
    def create_product_read_table_query(self, table_name: str) -> str:
        pass
