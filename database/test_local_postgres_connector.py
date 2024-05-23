from common.test_util import BaseTestCase
from database import config
from database.local_postgres_connector import LocalPostgresConnector


class TestLocalPostgresConnectorTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(BaseTestCase, self).setUp()
        self.local_connector = LocalPostgresConnector()

    def tearDown(self) -> None:
        self.local_connector.kill_all()

    def test_create_test_tables(self):
        expected_tables = {config.PRODUCT_READ_HISTORY_TABLE, config.PRODUCT_READ_CHANGES_TABLE,
                           config.AB_TEST_RUNS_TABLE, config.MERCHANTS_TABLE}
        actual_tables = self.local_connector.run_query(f"SELECT table_name FROM information_schema.tables "
                                                       f"WHERE table_schema='public' AND table_type='BASE TABLE';")
        actual_tables = {table['table_name'] for table in actual_tables}
        self.assertSetEqual(expected_tables, actual_tables)
