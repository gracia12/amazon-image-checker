import os

from common.test_util import BaseTestCase
from notification.slack_notifier import SlackNotificationManager


class TestSlackNotificationManager(BaseTestCase):
    def setUp(self) -> None:
        super(BaseTestCase, self).setUp()
        self.notification_manager = SlackNotificationManager()

    def test_send_message(self):
        temp_webhook_url = os.environ['SLACK_WEBHOOK_URL']
        self.notification_manager.webhook_url = ''
        with self.assertRaises(Exception):
            self.notification_manager.send_message('This is a test message please ignore')
        try:
            self.notification_manager.webhook_url = temp_webhook_url
            self.notification_manager.send_message('This is a test message please ignore')
        except Exception:
            self.fail()
