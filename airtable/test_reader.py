import os
from datetime import datetime
from unittest.mock import MagicMock

from freezegun import freeze_time

from airtable import config
from airtable.reader import AirtableReader
from common import test_util
from common.test_util import BaseTestCase
from test_ab_test_record import TestABTestRecordTestCase

ACTIVE_TEST_ID = 1
TEST_ASIN = 'B08LKMP5QX'


@freeze_time(datetime.strptime(TestABTestRecordTestCase.start_datetime, f'{config.PYTHON_DATETIME_TIMEZONE_FORMAT}'))
class BaseAirtableReaderTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(BaseAirtableReaderTestCase, self).setUp()
        self.airtable_reader = AirtableReader()

    def test_get_active_ab_tests(self):
        active_ab_tests = self.airtable_reader.get_active_ab_test_records()
        self.assertEqual(len(active_ab_tests), 1)
        self.assertEqual(active_ab_tests[ACTIVE_TEST_ID].fields[config.TEST_ID_FIELD], ACTIVE_TEST_ID)

    def test_get_flatfile_for_record(self):
        record = self.airtable_reader.get_active_ab_test_records()[ACTIVE_TEST_ID]
        record.current_variation = MagicMock(return_value='A')
        flatfile_for_record = record.get_flatfile_for_record()
        self.assertEqual(os.path.basename(test_util.TEST_FLATFILE_A), flatfile_for_record['filename'])

    def test_get_asins_with_active_ab_test(self):
        active_ab_tests = self.airtable_reader.get_active_ab_test_records()
        self.assertDictEqual(
            self.airtable_reader.get_asins_to_active_ab_test(), {TEST_ASIN: active_ab_tests[ACTIVE_TEST_ID]})
