import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from common import util
from scheduler.ab_test_task import ABTestTask

scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', hours=int(os.environ['SCHEDULER_INTERVAL_HOURS']))
def ab_test_task_scheduler():
    ABTestTask().run()


if __name__ == '__main__':
    util.initialize_logging(logging_level=logging.DEBUG)
    logging.info(f'Starting scheduler {os.path.basename(__file__)}')
    scheduler.start()
