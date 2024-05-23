from __future__ import annotations

import logging
import os
import time
import urllib.request
from io import FileIO, BytesIO
from typing import List, Optional

from dacite import from_dict
from sp_api.api import CatalogItems, Feeds, Products
from sp_api.base import FeedType
from sp_api.util import throttle_retry

from airtable.ab_test_record import ABTestRecord
from amazon_sp_api.amazon_util import AmazonUtil
from database.data_model import ASIN, ImageVariation, ABTestRun
from database.database_api import DatabaseApi


class AmazonApi:
    def __init__(self, database_api: DatabaseApi):
        self.last_merchant = None
        self.current_credentials: Optional[dict] = None
        self.database_api = database_api

    @throttle_retry()
    def get_images(self, asin: ASIN, ab_test_record: ABTestRecord) -> List[ImageVariation]:
        logging.debug(f'Getting images for asin: {asin}')
        self.init_credentials(ab_test_record=ab_test_record)
        response = CatalogItems(credentials=self.current_credentials).get_catalog_item(asin, includedData=['images'])
        images_response = response.payload['images'][0]['images']
        # convert dict to ImageVariation
        images = []
        for image in images_response:
            images.append(ImageVariation(image['variant'], image['link'], image['height'], image['width']))
        image_variations = [from_dict(ImageVariation, image) for image in images_response]
        unique_image_variations = sorted(list(set([image_variation.variant for image_variation in image_variations])))
        logging.info(f'Got {unique_image_variations} images for asin: {asin}')
        return image_variations

    @throttle_retry()
    def get_listing_price(self, asin: ASIN, ab_test_record: ABTestRecord) -> float | None:
        logging.debug(f'Getting price for asin: {asin}')
        self.init_credentials(ab_test_record=ab_test_record)
        response = Products(credentials=self.current_credentials).get_competitive_pricing_for_asins([asin])
        try:
            competitive_prices = response.payload[0]["Product"]["CompetitivePricing"]["CompetitivePrices"]
            logging.info(f'Payload for {asin} competitive pricing: {competitive_prices}')
            new_price = min(
                [price_data['Price']['ListingPrice']['Amount'] for price_data in competitive_prices if
                    price_data['condition'] == 'New'])
            return new_price
        except (KeyError, IndexError):
            logging.info(f'Missing pricing data for {asin}')
            return None
        except ValueError:
            logging.info(f'Missing pricing data for new items for {asin}')
            return None

    @throttle_retry()
    def is_active(self, asin: str, ab_test_record: ABTestRecord) -> bool | None:
        logging.debug(f'Checking isactive for: {asin}')
        self.init_credentials(ab_test_record=ab_test_record)
        response = Products(credentials=self.current_credentials).get_competitive_pricing_for_asins([asin])
        try:
            competitive_prices = response.payload[0]['Product']['CompetitivePricing']['CompetitivePrices']
            logging.info(f'Payload for {asin} pricing (for is active check): {competitive_prices}')
            return len(competitive_prices) > 0
        except (KeyError, IndexError):
            return None

    @throttle_retry()
    def post_feed(self, feed_url: str, ab_test_run: ABTestRun) -> int:
        logging.debug(f'Posting feed: {feed_url}')
        self.init_credentials(ab_test_run=ab_test_run)
        temp_file_path = self.read_xlsm_url_into_temp_file(feed_url)
        try:
            response = Feeds(credentials=self.current_credentials).submit_feed(
                FeedType.POST_FLAT_FILE_LISTINGS_DATA, FileIO(temp_file_path),
                content_type='application/vnd.ms-excel.sheet.macroEnabled.12')
        except Exception as e:
            os.remove(temp_file_path)
            raise e
        finally:
            os.remove(temp_file_path)
        logging.debug(f'Payload for feed {feed_url} is {response[1].payload}')
        payload_feed_id = int(response[1].payload['feedId'])
        logging.info(f'Got feed_id: {payload_feed_id} for {feed_url}')
        return payload_feed_id

    @staticmethod
    def read_xlsm_url_into_temp_file(feed_url: str) -> str:
        if feed_url.startswith('http'):
            with urllib.request.urlopen(feed_url) as url_response:
                url_content = url_response.read()
            bytes_io = BytesIO(url_content)
        else:
            with open(feed_url, 'rb') as local_file:
                bytes_io = BytesIO(local_file.read())
        temp_file_path = f'{int(time.time())}.xlsm'
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(bytes_io.read())
        return temp_file_path

    def init_credentials(self, ab_test_record: ABTestRecord = None, ab_test_run: ABTestRun = None):
        assert ab_test_record or ab_test_run
        merchant = AmazonUtil.extract_merchant(ab_test_record, ab_test_run)
        if self.last_merchant == merchant:
            return self.current_credentials
        credentials_from_db = self.database_api.get_credentials_from_merchant(merchant)
        # https://python-amazon-sp-api.readthedocs.io/en/latest/from_code/
        self.current_credentials = dict(
            refresh_token=credentials_from_db.sp_api_refresh_token,
            lwa_app_id=credentials_from_db.lwa_app_id,
            lwa_client_secret=credentials_from_db.lwa_client_secret,
            aws_secret_key=credentials_from_db.sp_api_secret_key,
            aws_access_key=credentials_from_db.sp_api_access_key,
            role_arn=credentials_from_db.sp_api_role_arn,
        )
