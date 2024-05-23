import logging
from datetime import datetime

from airtable.reader import AirtableReader
from amazon_sp_api.amazon_api import AmazonApi
from database.database_api import DatabaseApi
from database.postgres_connector import PostgresConnector


class BaseTask:
    def __init__(self):
        self.database_api = DatabaseApi(PostgresConnector())
        self.airtable_reader = AirtableReader()
        self.amazon_api = AmazonApi(self.database_api)

    def task(self):
        pass

    def run(self):
        logging.info(f'Running {self.__class__.__name__}  time is {datetime.utcnow()}')
        self.task()
