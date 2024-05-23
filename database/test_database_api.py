from __future__ import annotations

from database.base_connector_test_case import BaseConnectorTestCase
from database.data_model import CredentialsSPApi


class TestDatabaseApi(BaseConnectorTestCase):
    def test_get_last_product_read_empty_table(self):
        last_product_read = self.database_api.get_last_product_read(self.asin_active, self.ab_test_record1)
        self.assertEqual(last_product_read, None)

    def test_get_last_product_read(self):
        self.database_api.insert_product_read(self.product_read_yesterday)
        self.assertEqual(self.database_api.get_last_product_read(self.asin_active, self.ab_test_record1),
                         self.product_read_yesterday)
        self.database_api.insert_product_read(self.product_read_today)
        self.assertEqual(self.database_api.get_last_product_read(self.asin_active, self.ab_test_record1),
                         self.product_read_today)

    def test_insert_product_read_changes(self):
        self.database_api.insert_product_read_changes(self.product_read_diff)
        changes_from_db = self.database_api.get_last_product_read_changes(self.asin_active, self.ab_test_record1)
        self.assertEqual(self.product_read_diff, changes_from_db)

    def test_insert_product_read_changes_no_price_diff(self):
        self.product_read_diff.listing_price = None
        self.database_api.insert_product_read_changes(self.product_read_diff)
        changes_from_db = self.database_api.get_last_product_read_changes(self.asin_active, self.ab_test_record1)
        self.assertIsNone(changes_from_db.listing_price)
        self.assertEqual(self.product_read_diff, changes_from_db)

    def test_insert_product_read_changes_no_image_variations_diff(self):
        self.product_read_diff.image_variations = []
        self.database_api.insert_product_read_changes(self.product_read_diff)
        changes_from_db = self.database_api.get_last_product_read_changes(self.asin_active, self.ab_test_record1)
        self.assertListEqual(changes_from_db.image_variations, [])
        self.assertEqual(self.product_read_diff, changes_from_db)

    def test_insert_product_read_changes_missing_in_active(self):
        self.product_read_diff.is_active = None
        self.database_api.insert_product_read_changes(self.product_read_diff)
        changes_from_db = self.database_api.get_last_product_read_changes(self.asin_active, self.ab_test_record1)
        self.assertIsNone(changes_from_db.is_active)
        self.assertEqual(self.product_read_diff, changes_from_db)

    def test_update_feed_id(self):
        self.database_api.insert_ab_test_run(self.ab_test_run1a)
        self.assertIsNone(self.database_api.get_last_run_for_ab_test(self.ab_test_record1).feed_id)
        self.database_api.update_feed_id(self.ab_test_run1a)
        self.assertEqual(self.get_feed_id_by_run_id(self.ab_test_run1a.run_id), self.ab_test_run1a.feed_id)
        self.database_api.insert_ab_test_run(self.ab_test_run1b)
        self.database_api.insert_ab_test_run(self.ab_test_run2a)
        self.assertIsNone(self.database_api.get_last_run_for_ab_test(self.ab_test_record1).feed_id)
        self.database_api.update_feed_id(self.ab_test_run1b)
        self.assertEqual(self.get_feed_id_by_run_id(self.ab_test_run1b.run_id), self.ab_test_run1b.feed_id)
        self.assertEqual(self.get_feed_id_by_run_id(self.ab_test_run1a.run_id), self.ab_test_run1a.feed_id)
        self.assertIsNone(self.database_api.get_last_run_for_ab_test(self.ab_test_record2).feed_id)

    def test_get_last_run_for_ab_test(self):
        self.ab_test_run1a.feed_id = None
        inserted_ab_test_run = self.database_api.insert_ab_test_run(self.ab_test_run1a)
        self.assertEqual(self.ab_test_run1a.run_id, inserted_ab_test_run.run_id)
        self.assertEqual(self.database_api.get_last_run_for_ab_test(self.ab_test_record1), self.ab_test_run1a)

        self.ab_test_run1b.feed_id = None
        self.database_api.insert_ab_test_run(self.ab_test_run1b)
        self.assertEqual(self.database_api.get_last_run_for_ab_test(self.ab_test_record1), self.ab_test_run1b)

    def get_last_run_for_ab_test_no_runs(self):
        self.database_api.insert_ab_test_run(self.ab_test_run1a)
        self.assertEqual(self.database_api.get_last_run_for_ab_test(self.ab_test_record2), None)

    def test_get_credentials_from_merchant(self):
        merchant2 = self.merchant + '2'
        credetials_lwa1 = CredentialsSPApi(
            'app_id1', 'client_secret1', 'access_key1', 'refresh1', 'sp_api_secret1',
            'arn1')
        credetials_lwa2 = CredentialsSPApi(
            'app_id2', 'client_secret2', 'access_key2', 'refresh2', 'sp_api_secret2',
            'arn2')
        self.insert_credentials(self.merchant, credetials_lwa1)
        self.insert_credentials(merchant2, credetials_lwa2)
        actual_credentials = self.database_api.get_credentials_from_merchant(self.merchant)
        self.assertEqual(actual_credentials, credetials_lwa1)
