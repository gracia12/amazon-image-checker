import logging

import airtable.config
from airtable.ab_test_record import ABTestRecord
from common import util
from database.data_model import ABTestRun
from scheduler.base_task import BaseTask


class ABTestTask(BaseTask):
    def should_run_ab_test(self, ab_test_record: ABTestRecord) -> bool:
        last_ab_test_run = self.database_api.get_last_run_for_ab_test(ab_test_record)
        current_variation = ab_test_record.current_variation()
        if not last_ab_test_run and current_variation == 'B':
            return True
        return last_ab_test_run and last_ab_test_run.variation != current_variation

    def task(self):
        active_ab_test_records = self.airtable_reader.get_active_ab_test_records()
        for ab_test_record in active_ab_test_records.values():
            is_going_to_run_ab_test = self.should_run_ab_test(ab_test_record)
            logging.info(
                f'Test ID {ab_test_record.fields[airtable.config.TEST_ID_FIELD]} should run = '
                f'{str(is_going_to_run_ab_test)}')
            if is_going_to_run_ab_test:
                self.run_ab_test(ab_test_record)

    def run_ab_test(self, ab_test_record: ABTestRecord):
        ab_test_run = ABTestRun.from_record(ab_test_record)
        logging.debug(f'Running AB test: {ab_test_run}')
        ab_test_run = self.database_api.insert_ab_test_run(ab_test_run)
        ab_test_run.feed_id = self.amazon_api.post_feed(
            ab_test_record.get_flatfile_url_for_record(), ab_test_run)
        self.database_api.update_feed_id(ab_test_run)
        logging.info(f'Finished running AB test: {ab_test_run}')


if __name__ == '__main__':
    util.initialize_logging(logging_level=logging.DEBUG)
    ABTestTask().run()
