import logging
import os
from datetime import datetime
from typing import Mapping

import pandas as pd
from pyairtable import Table

from airtable import config
from airtable.ab_test_record import ABTestRecord, ABTestId
from database.data_model import ASIN


class AirtableReader():
    def __init__(self):
        self.table = Table(os.environ['AIRTABLE_API_KEY'], os.environ['AIRTABLE_BASE_ID'], os.environ['AIRTABLE_TABLE'])

    def get_active_ab_test_records(self) -> Mapping[ABTestId, ABTestRecord]:
        active_ab_test_formula = AirtableReader._active_ab_test_formula()
        logging.debug(f'Getting active AB tests from Airtable with formula: {active_ab_test_formula}')
        active_ab_tests = self.table.all(formula=active_ab_test_formula)
        test_id_to_records = {self._get_raw_record_id(raw_record): ABTestRecord(self._get_raw_record_fields(raw_record))
            for raw_record in active_ab_tests}
        logging.debug(
            f'Found {len(test_id_to_records)} active AB tests with IDs: '
            f'{", ".join([str(test_id) for test_id in test_id_to_records.keys()])}')
        return test_id_to_records

    def get_asins_to_active_ab_test(self) -> Mapping[ASIN, ABTestRecord]:
        asin_to_ab_test_records = {}
        for ab_test_record in self.get_active_ab_test_records().values():
            flatfile_url = ab_test_record.get_flatfile_url_for_record()
            ab_test_df = pd.read_excel(flatfile_url, sheet_name=config.FLATFILE_SHEET_NAME, skiprows=[0, 2]).dropna(
                how='all')
            ab_test_asins = ab_test_df[config.FLATFILE_ASIN_COLUMN].dropna().tolist()
            asin_to_ab_test_records.update({asin: ab_test_record for asin in ab_test_asins})
        return asin_to_ab_test_records

    @staticmethod
    def _get_raw_record_fields(record: dict) -> dict:
        return record['fields']

    @staticmethod
    def _active_ab_test_formula() -> str:
        now_str = f'DATETIME_PARSE(\"' \
                  f'{datetime.utcnow().astimezone(ABTestRecord.amazon_timezone).strftime(config.PYTHON_DATETIME_FORMAT)}\", ' \
                  f'\"YYYY-MM-DD hh:mm\")'
        now_after_start_formula = f'IS_AFTER({now_str}, {{{config.START_DATE_FIELD}}})'
        now_before_end_formula = f'IS_BEFORE({now_str}, {{{config.END_DATE_FIELD}}})'
        between_dates_formula = f'AND({now_after_start_formula},{now_before_end_formula})'
        active_status_formula = f'{{{config.STATUS_FIELD}}} = \"Active\"'
        final_formula = f'AND({between_dates_formula},{active_status_formula})'
        return final_formula

    def _get_raw_record_id(self, record: dict) -> ABTestId:
        return self._get_raw_record_fields(record)[config.TEST_ID_FIELD]
