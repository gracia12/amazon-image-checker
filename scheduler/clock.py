import os
import sys
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

import sys
sys.path.append('D:/ODZ Services/Projects/amazon-image-checker-master')

from common import util
from scheduler.ab_test_task import ABTestTask
from scheduler.product_read_changes_task import ProductReadChangesTask



scheduler = BlockingScheduler()
@scheduler.scheduled_job('interval', minutes=15)
def product_read_changes_task_scheduler():
    ProductReadChangesTask().run()


@scheduler.scheduled_job('interval', minutes=30)
def ab_test_task_scheduler():
    ABTestTask().run()


if __name__ == '__main__':
    util.initialize_logging()
    logging.info('Starting scheduler')
    scheduler.start()





