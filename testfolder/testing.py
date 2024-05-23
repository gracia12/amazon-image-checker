import os
from dotenv import load_dotenv


load_dotenv()

webhook_url = os.getenv('SLACK_WEBHOOK_URL')
print(webhook_url)
webhook_url = os.environ['SLACK_WEBHOOK_URL']
print(webhook_url)