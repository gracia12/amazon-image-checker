from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pytz import timezone

from airtable import config


@dataclass
class ABTestRecord:
    fields: dict
    amazon_timezone = timezone(config.AMAZON_TIMEZONE_NAME)
    amazon_timezone_str = timezone(config.AMAZON_TIMEZONE_NAME).localize(datetime.utcnow()).strftime('%z')

    def _start_date_to_datetime(self) -> datetime:
        return datetime.strptime(
            f'{self.fields[config.START_DATE_FIELD]} {ABTestRecord.amazon_timezone_str}',
            config.AIRTABLE_DATETIME_TIMEZONE_FORMAT)

    def _calculate_hours_since_start(self) -> float:
        amazon_time = datetime.utcnow().astimezone(ABTestRecord.amazon_timezone)
        start_date = self._start_date_to_datetime()
        hours_since_start = (amazon_time - start_date).total_seconds() / 3600
        # logging_format = '%H:%M%z(%a)'
        # logging.info(
        #     f'ID={self.fields[config.TEST_ID_FIELD]}, '
        #     f'amz_time={amazon_time.strftime(logging_format)}, start_date={start_date.strftime(logging_format)}, '
        #     f'hr_diff={round(hours_since_start, 1)}, utc_now={datetime.utcnow().strftime(logging_format)}')
        return hours_since_start

    def current_variation(self) -> str:
        hours_since_start = self._calculate_hours_since_start()
        rotations = int(hours_since_start / self.fields[config.ROTATION_FIELD])
        return 'B' if rotations % 2 else 'A'

    def get_flatfile_for_record(self) -> dict:
        flatfile = self.fields[config.FLATFILE_FIELD[self.current_variation()]][0]
        return flatfile

    def get_flatfile_url_for_record(self) -> str:
        return self.get_flatfile_for_record()['url']


ABTestId = int
