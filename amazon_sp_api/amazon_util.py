from __future__ import annotations

import airtable.config
from airtable.ab_test_record import ABTestRecord
from database.data_model import ASIN, ABTestRun


class AmazonUtil:

    @staticmethod
    def get_url_from_asin(asin: ASIN) -> str:
        url = 'https://www.amazon.com/dp/' + asin
        return url

    @staticmethod
    def extract_merchant(ab_test_record: ABTestRecord | None, ab_test_run: ABTestRun | None) -> str:
        if ab_test_record:
            return ab_test_record.fields[airtable.config.MERCHANT_FIELD]
        elif ab_test_run:
            return ab_test_run.merchant
