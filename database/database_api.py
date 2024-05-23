from __future__ import annotations

import copy
from dataclasses import asdict

import airtable.config
from airtable.ab_test_record import ABTestRecord
from database import config
from database.base_connector import BaseConnector
from database.data_model import SQLQuery, ASIN, ImageVariation, ProductRead, CredentialsSPApi, ABTestRun, \
    ProductReadDiff


class DatabaseApi:
    def __init__(self, connector: BaseConnector):
        self.connector = connector

    @staticmethod
    def _last_product_read_query(asin: ASIN, ab_test_record: ABTestRecord, table_name: str) -> SQLQuery:
        query = f"SELECT {config.IMAGE_VARIATIONS_FIELD}, {config.ASIN_FIELD}, {config.READ_TIME_FIELD}, " \
                f"{config.LISTING_PRICE_FIELD}, {config.IS_ACTIVE_FIELD}, {config.MERCHANT_FIELD} " \
                f"FROM {table_name} " \
                f"WHERE {config.ASIN_FIELD}  = '{asin}' AND " \
                f"{config.MERCHANT_FIELD} = '{ab_test_record.fields[airtable.config.MERCHANT_FIELD]}' " \
                f"ORDER BY {config.READ_TIME_FIELD} DESC LIMIT 1"
        return query

    def get_last_product_read(self, asin: ASIN, ab_test_record: ABTestRecord,
                              table_name: str = None) -> ProductRead | None:
        table_name = table_name if table_name else config.PRODUCT_READ_HISTORY_TABLE
        results = self.connector.run_query(DatabaseApi._last_product_read_query(asin, ab_test_record, table_name))
        if results:
            last_product_read = DatabaseApi._parse_query_result_row_to_product_read(results[0])
            return last_product_read
        return None

    @staticmethod
    def _parse_query_result_row_to_product_read(result_row: dict) -> ProductRead:
        if config.IMAGE_VARIATIONS_FIELD in result_row and isinstance(result_row[config.IMAGE_VARIATIONS_FIELD], list):
            image_variations_list = [
                ImageVariation(**image_variation) for image_variation in result_row[
                    config.IMAGE_VARIATIONS_FIELD]]
        else:
            image_variations_list = []
        listing_price = result_row[config.LISTING_PRICE_FIELD] if config.LISTING_PRICE_FIELD in result_row else None
        is_active = result_row[config.IS_ACTIVE_FIELD] if config.IS_ACTIVE_FIELD in result_row else None
        product_read = ProductRead(
            asin=result_row[config.ASIN_FIELD], read_time=result_row[config.READ_TIME_FIELD],
            image_variations=image_variations_list, listing_price=listing_price,
            merchant=result_row[config.MERCHANT_FIELD], is_active=is_active)
        return product_read

    @staticmethod
    def _insert_product_read_query(product_read: ProductRead, table_name: str):
        # convert image_variations from list to str matching the format in the database
        assert product_read.image_variations or product_read.listing_price
        columns = f"({config.ASIN_FIELD}" \
                  f"{', ' + config.IMAGE_VARIATIONS_FIELD if product_read.image_variations else ''}" \
                  f", {config.READ_TIME_FIELD}" \
                  f"{', ' + config.LISTING_PRICE_FIELD if product_read.listing_price else ''}" \
                  f"{', ' + config.IS_ACTIVE_FIELD if product_read.is_active is not None else ''}" \
                  f", {config.MERCHANT_FIELD}) "
        values = f"VALUES ('{product_read.asin}'"
        if product_read.image_variations:
            image_variations_json = DatabaseApi._prepare_json_to_sql_insert_query(product_read)
            values += f", '{image_variations_json}'"
        values += f", '{product_read.read_time}'"
        if product_read.listing_price:
            values += f", {product_read.listing_price}"
        if product_read.is_active is not None:
            values += f", {product_read.is_active}"
        values += f", '{product_read.merchant}')"
        query = f"INSERT INTO {table_name} {columns} {values}"
        return query

    @staticmethod
    def _prepare_json_to_sql_insert_query(product_read: ProductRead) -> SQLQuery:
        assert product_read.image_variations
        return str(asdict(product_read)['image_variations']).replace("'", '"')

    def insert_product_read(self, product_read: ProductRead, table_name: str = None):
        table_name = table_name or config.PRODUCT_READ_HISTORY_TABLE
        self.connector.run_query(DatabaseApi._insert_product_read_query(product_read, table_name))

    def insert_product_read_changes(self, product_read_diff: ProductReadDiff):
        assert product_read_diff.has_diff()
        self.insert_product_read(product_read_diff, config.PRODUCT_READ_CHANGES_TABLE)

    def get_last_product_read_changes(self, asin: ASIN, ab_test_record: ABTestRecord) -> ProductReadDiff | None:
        product_read_maybe = self.get_last_product_read(asin, ab_test_record, config.PRODUCT_READ_CHANGES_TABLE)
        if product_read_maybe:
            return ProductReadDiff(product_read_maybe)
        return None

    def _insert_ab_test_run_query(self, ab_test_run: ABTestRun) -> SQLQuery:
        query = f"INSERT INTO {config.AB_TEST_RUNS_TABLE} " \
                f"({config.AB_TEST_ID_FIELD}, {config.RUN_TIME_FIELD}, {config.VARIATION_FIELD}, " \
                f"{config.MERCHANT_FIELD}) " \
                f"VALUES ('{ab_test_run.test_id}', '{ab_test_run.run_time}', '{ab_test_run.variation}', " \
                f"'{ab_test_run.merchant}')"
        return query

    def _get_inserted_ab_test_run_id_query(self, ab_test_run: ABTestRun) -> SQLQuery:
        query = f"SELECT {config.RUN_ID_FIELD} FROM {config.AB_TEST_RUNS_TABLE} " \
                f"WHERE {config.AB_TEST_ID_FIELD} = '{ab_test_run.test_id}' " \
                f"ORDER BY {config.RUN_ID_FIELD} DESC LIMIT 1 "
        return query

    def insert_ab_test_run(self, ab_test_run: ABTestRun) -> ABTestRun:
        self.connector.run_query(self._insert_ab_test_run_query(ab_test_run))
        inserted_run_id = self.connector.run_query(self._get_inserted_ab_test_run_id_query(ab_test_run))[0][
            config.RUN_ID_FIELD]
        inserted_ab_test_run = copy.deepcopy(ab_test_run)
        inserted_ab_test_run.run_id = inserted_run_id
        return inserted_ab_test_run

    def _last_run_for_ab_test_query(self, ab_test_record: ABTestRecord) -> SQLQuery:
        query = f"SELECT {config.AB_TEST_ID_FIELD}, {config.MERCHANT_FIELD}, {config.RUN_TIME_FIELD}," \
                f" {config.VARIATION_FIELD}, {config.FEED_ID_FIELD}, {config.RUN_ID_FIELD} " \
                f"FROM {config.AB_TEST_RUNS_TABLE} " \
                f"WHERE {config.AB_TEST_ID_FIELD}  = '{ab_test_record.fields[airtable.config.TEST_ID_FIELD]}'" \
                f" AND {config.MERCHANT_FIELD} = '{ab_test_record.fields[airtable.config.MERCHANT_FIELD]}' " \
                f"ORDER BY {config.RUN_ID_FIELD} DESC LIMIT 1"
        return query

    def _parse_query_result_row_to_ab_test_run(self, result_row: dict) -> ABTestRun:
        ab_test_run = ABTestRun(
            test_id=result_row[config.AB_TEST_ID_FIELD], run_time=result_row[config.RUN_TIME_FIELD],
            variation=result_row[config.VARIATION_FIELD], merchant=result_row[config.MERCHANT_FIELD],
            run_id=result_row[config.RUN_ID_FIELD], feed_id=result_row[config.FEED_ID_FIELD])
        return ab_test_run

    def get_last_run_for_ab_test(self, ab_test_record: ABTestRecord) -> ABTestRun | None:
        results = self.connector.run_query(self._last_run_for_ab_test_query(ab_test_record))
        if results:
            last_ab_test_run = self._parse_query_result_row_to_ab_test_run(results[0])
            return last_ab_test_run
        return None

    def _update_feed_id_query(self, ab_test_run: ABTestRun) -> SQLQuery:
        query = f"UPDATE {config.AB_TEST_RUNS_TABLE} " \
                f"SET {config.FEED_ID_FIELD} = '{ab_test_run.feed_id}' " \
                f"WHERE {config.RUN_ID_FIELD} = (" \
                f"SELECT {config.RUN_ID_FIELD} FROM {config.AB_TEST_RUNS_TABLE} " \
                f"WHERE {config.AB_TEST_ID_FIELD} = '{ab_test_run.test_id}' " \
                f"ORDER BY {config.RUN_ID_FIELD} DESC LIMIT 1)"
        return query

    def update_feed_id(self, ab_test_run: ABTestRun):
        self.connector.run_query(self._update_feed_id_query(ab_test_run))

    def _credentials_from_merchant_query(self, merchant: str) -> SQLQuery:
        query = f"SELECT {config.LWA_APP_ID_FIELD}, {config.LWA_CLIENT_SECRET_FIELD}, " \
                f"{config.SP_API_SECRET_KEY_FIELD}, {config.SP_API_ROLE_ARN_FIELD}, " \
                f"{config.SP_API_ACCESS_KEY_FIELD}, {config.SP_API_REFRESH_TOKEN_FIELD} " \
                f"FROM {config.MERCHANTS_TABLE} " \
                f"WHERE {config.MERCHANT_FIELD} = '{merchant}'"
        return query

    def _parse_credentials_lwa(self, result_row: dict) -> CredentialsSPApi:
        return CredentialsSPApi(lwa_app_id=result_row[config.LWA_APP_ID_FIELD],
                                lwa_client_secret=result_row[config.LWA_CLIENT_SECRET_FIELD],
                                sp_api_secret_key=result_row[config.SP_API_SECRET_KEY_FIELD],
                                sp_api_role_arn=result_row[config.SP_API_ROLE_ARN_FIELD],
                                sp_api_access_key=result_row[config.SP_API_ACCESS_KEY_FIELD],
                                sp_api_refresh_token=result_row[config.SP_API_REFRESH_TOKEN_FIELD])

    def get_credentials_from_merchant(self, merchant: str) -> CredentialsSPApi:
        results = self.connector.run_query(self._credentials_from_merchant_query(merchant), verbose=False)
        return self._parse_credentials_lwa(results[0])
