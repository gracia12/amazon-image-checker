from copy import deepcopy
from unittest.mock import MagicMock

from database.test_database_api import BaseConnectorTestCase
from scheduler.product_read_changes_task import ProductReadChangesTask


class TestProductReadChangesTask(BaseConnectorTestCase):
    def setUp(self) -> None:
        super(TestProductReadChangesTask, self).setUp()
        self.product_read_changes_task = ProductReadChangesTask()
        self.product_read_changes_task.database_api = self.local_connector
        self.product_read_changes_task.amazon_api = MagicMock()
        self.product_read_changes_task.notification_manager = MagicMock()

    def test_process_asin(self):
        self.product_read_changes_task.generate_product_read = MagicMock(return_value=self.product_read_today)

        self.product_read_changes_task.database_api.get_last_product_read = MagicMock(return_value=None)
        self.product_read_changes_task.process_product_read_changed = MagicMock()
        self.product_read_changes_task.database_api.insert_product_read = MagicMock()
        self.product_read_changes_task.process_asin(self.asin_active, self.ab_test_record1)
        self.product_read_changes_task.process_product_read_changed.assert_not_called()
        self.product_read_changes_task.database_api.insert_product_read.assert_called()

        self.product_read_changes_task.database_api.get_last_product_read = MagicMock(
            return_value=self.product_read_yesterday)
        self.product_read_changes_task.process_product_read_changed = MagicMock()
        self.product_read_changes_task.database_api.insert_product_read = MagicMock()
        self.product_read_changes_task.process_asin(self.asin_active, self.ab_test_record1)
        self.product_read_changes_task.process_product_read_changed.assert_called()
        self.product_read_changes_task.database_api.insert_product_read.assert_called()

        product_read_today_yesterday = deepcopy(self.product_read_today)
        product_read_today_yesterday.read_time = self.product_read_yesterday.read_time
        self.product_read_changes_task.database_api.get_last_product_read = MagicMock(
            return_value=product_read_today_yesterday)
        self.product_read_changes_task.process_product_read_changed = MagicMock()
        self.product_read_changes_task.database_api.insert_product_read = MagicMock()
        self.product_read_changes_task.process_asin(self.asin_active, self.ab_test_record1)
        self.product_read_changes_task.process_product_read_changed.assert_not_called()
        self.product_read_changes_task.database_api.insert_product_read.assert_not_called()
