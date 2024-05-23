import json
import logging
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

class SlackNotificationManager:
    webhook_url = os.environ['SLACK_WEBHOOK_URL']
    # print(webhook_url)

    def send_message(self, message: str):
        logging.debug(f'Notifying {message}')
        slack_data = {'text': message}
        byte_length = str(sys.getsizeof(slack_data))
        headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
        response = requests.post(self.webhook_url, data=json.dumps(slack_data), headers=headers)
        if response.status_code != 200:
            logging.error(f'{response.status_code} - {response.text}')
