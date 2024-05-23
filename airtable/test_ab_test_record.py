import copy
from datetime import datetime, timedelta

from freezegun import freeze_time

from airtable import config
from airtable.ab_test_record import ABTestRecord
from common.test_util import BaseTestCase


class TestABTestRecordTestCase(BaseTestCase):
    start_date = '2023-01-16'
    start_datetime = f'{start_date} 04:01 {ABTestRecord.amazon_timezone_str}'

    def test_current_variation(self):
        record1 = ABTestRecord(
            {
                config.TEST_ID_FIELD: 1,
                config.ROTATION_FIELD: 24,
                config.START_DATE_FIELD: TestABTestRecordTestCase.start_date})
        record2 = copy.deepcopy(record1)
        record2.fields[config.ROTATION_FIELD] = 48
        with freeze_time(
                datetime.strptime(
                    TestABTestRecordTestCase.start_datetime, f'{config.PYTHON_DATETIME_TIMEZONE_FORMAT}')):
            self.assertEqual(record1.current_variation(), 'A')
            self.assertEqual(record2.current_variation(), 'A')
        with freeze_time(
                datetime.strptime(
                    TestABTestRecordTestCase.start_datetime,
                    f'{config.PYTHON_DATETIME_TIMEZONE_FORMAT}') + timedelta(days=1)):
            self.assertEqual(record1.current_variation(), 'B')
            self.assertEqual(record2.current_variation(), 'A')
