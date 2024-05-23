import logging
from datetime import datetime

import airtable.config
from airtable.ab_test_record import ABTestRecord
from amazon_sp_api.amazon_util import AmazonUtil
from common import util
from database.data_model import ASIN, ProductRead, ProductReadDiff
from notification.slack_notifier import SlackNotificationManager
from scheduler.base_task import BaseTask


class ProductReadChangesTask(BaseTask):
    def __init__(self):
        self.notification_manager = SlackNotificationManager()
        super(ProductReadChangesTask, self).__init__()

    def task(self):
        asins_to_active_ab_test = self.airtable_reader.get_asins_to_active_ab_test()
        for asin, ab_test_record in asins_to_active_ab_test.items():
            self.process_asin(asin, ab_test_record)

    def process_asin(self, asin: ASIN, ab_test_record: ABTestRecord):
        logging.debug('Processing asin {}'.format(asin))
        last_product_read = self.database_api.get_last_product_read(asin, ab_test_record)
        current_product_read = self.generate_product_read(ab_test_record, asin)
        product_read_diff = ProductReadDiff(current_product_read, last_product_read)
        if product_read_diff.has_diff() and last_product_read:
            self.process_product_read_changed(product_read_diff, ab_test_record)
        if last_product_read is None or product_read_diff.has_diff():
            self.database_api.insert_product_read(current_product_read)

    def process_product_read_changed(self, product_read_diff: ProductReadDiff, ab_test_record: ABTestRecord):
        images_changed = set([image_variation.variant for image_variation in product_read_diff.image_variations])
        logging.info(
            f'Found product read changes for asin {product_read_diff.asin}'
            f'{" in images " if images_changed else ""}{", ".join(images_changed)}'
            f'{" in listing price " + str(product_read_diff.listing_price) if product_read_diff.listing_price else ""}'
            f'{" in is_active " + str(product_read_diff.is_active) if product_read_diff.is_active is not None else ""}')
        self.database_api.insert_product_read_changes(product_read_diff)
        notification_message = self.create_message_for_product_read_changes(product_read_diff, ab_test_record)
        self.notification_manager.send_message(notification_message)

    def create_message_for_product_read_changes(
            self, product_read_diff: ProductReadDiff, ab_test_record: ABTestRecord) -> str:
        asin_url = AmazonUtil.get_url_from_asin(product_read_diff.asin)
        asin_url_formatted = f'<{asin_url}|{product_read_diff.asin}>'
        change_message = f'{asin_url_formatted} ({ab_test_record.fields[airtable.config.MERCHANT_FIELD]}, test ID=' \
                         f'{ab_test_record.fields[airtable.config.TEST_ID_FIELD]}):'
        if product_read_diff.image_variations:
            variations_with_diff = set(
                [image_variation.variant for image_variation in product_read_diff.image_variations])
            change_message += f' changed images {", ".join(variations_with_diff)}'
        if product_read_diff.listing_price:
            change_message += f' changed price to {product_read_diff.listing_price}'
        if product_read_diff.is_active is not None:
            change_message += f' changed status to {"ACTIVE" if product_read_diff.is_active else "INACTIVE"}'
        return change_message

    def generate_product_read(self, ab_test_record: ABTestRecord, asin: ASIN) -> ProductRead:
        read_time = datetime.utcnow()
        images = self.amazon_api.get_images(asin, ab_test_record)
        listing_price = self.amazon_api.get_listing_price(asin, ab_test_record)
        is_active = self.amazon_api.is_active(asin, ab_test_record)
        new_product_read = ProductRead(
            asin, read_time, images, listing_price,
            ab_test_record.fields[airtable.config.MERCHANT_FIELD], is_active)
        return new_product_read


if __name__ == '__main__':
    util.initialize_logging(logging_level=logging.DEBUG)
    ProductReadChangesTask().run()
