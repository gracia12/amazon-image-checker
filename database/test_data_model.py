import copy
from datetime import datetime, timedelta

from data_model import ProductReadDiff, ProductRead, ImageVariation
from test_util import BaseTestCase


class TestProductReadDiff(BaseTestCase):
    def setUp(self) -> None:
        super(TestProductReadDiff, self).setUp()
        self.product_read1 = ProductRead(
            'asin', datetime.today(), [
                ImageVariation('MAIN', 'https://m.media-amazon.com/images/I/51Zy9Z9Z1a.jpg', 2500, 2500),
                ImageVariation('PT01', 'https://m.media-amazon.com/images/I/51Zy9Z9Z1b.jpg', 500, 500)],
            1.0, 'merchant', True)
        self.product_read2 = copy.deepcopy(self.product_read1)
        self.product_read2.read_time -= timedelta(days=1)

    def test_diff_asin_raises_error(self):
        self.product_read2.asin = 'asin2'
        with self.assertRaises(AssertionError) as err:
            ProductReadDiff(self.product_read1, self.product_read2)

    def test_has_diff_no_diff(self):
        diff = ProductReadDiff(self.product_read1, self.product_read2)
        self.assertFalse(diff.has_diff())
        self.assertListEqual(diff.image_variations, [])
        self.assertIsNone(diff.is_active)
        self.assertIsNone(diff.listing_price)

    def test_has_diff_image_variations(self):
        self.product_read2.image_variations[0].link += '2'
        diff = ProductReadDiff(self.product_read1, self.product_read2)
        self.assertTrue(diff.has_diff())
        self.assertEqual(diff.image_variations, [self.product_read1.image_variations[0]])

    def test_has_diff_listing_price(self):
        self.product_read2.listing_price += 1
        diff = ProductReadDiff(self.product_read1, self.product_read2)
        self.assertTrue(diff.has_diff())
        self.assertEqual(diff.listing_price, self.product_read1.listing_price)

        self.product_read2.listing_price = None
        diff = ProductReadDiff(self.product_read1, self.product_read2)
        self.assertFalse(diff.has_diff())
        self.assertIsNone(diff.listing_price)

    def test_has_diff_is_active(self):
        self.product_read2.is_active = not self.product_read1.is_active
        diff = ProductReadDiff(self.product_read1, self.product_read2)
        self.assertTrue(diff.has_diff())
        self.assertEqual(diff.is_active, self.product_read1.is_active)

        self.product_read2.is_active = None
        diff = ProductReadDiff(self.product_read1, self.product_read2)
        self.assertFalse(diff.has_diff())
        self.assertIsNone(diff.is_active)
