from amazon_sp_api.amazon_api import AmazonApi
from common import test_util
from database.base_connector_test_case import BaseConnectorTestCase

# Need to refresh the asin to an active one sometimes
TEST_ASIN = 'B08JYC691S'
TEST_PRICE = 11.99


# TEST_SKU = 'TF-W-THIN-7P8-07'
# INACTIVE_SKU = 'TF-M-EG-TL-HPAT-8MM-P-1P-2-14.5'
# INACTIVE_ASIN = 'B09Z2C8W9V'

class TestAmazonApi(BaseConnectorTestCase):
    def setUp(self) -> None:
        super(TestAmazonApi, self).setUp()
        self.amazon_api = AmazonApi(self.database_api)
        self.insert_credentials(self.merchant, self.default_credentials())

    def test_get_images(self):
        images = self.amazon_api.get_images(TEST_ASIN, self.ab_test_record1)
        self.assertTrue(len(images))
        self.assertTrue(images[0].link.startswith('https://m.media-amazon.com/images/I/'))

    def test_submit_feed(self):
        self.assertIsInstance(self.amazon_api.post_feed(test_util.TEST_FLATFILE_A, self.ab_test_run1a), int)

    def test_get_listing_price(self):
        self.assertTrue(self.amazon_api.get_listing_price(TEST_ASIN, self.ab_test_record1) > 0)
        self.assertIsNone(self.amazon_api.get_listing_price('BBBBBBBBB', self.ab_test_record1))

    def test_is_active(self):
        self.assertTrue(self.amazon_api.is_active(TEST_ASIN, self.ab_test_record1))
        self.assertIsNone(self.amazon_api.is_active('BBBBBBBBB', self.ab_test_record1))
