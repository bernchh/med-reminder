import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Twilio authenticated client account.
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_text_message(to, body):
    client.messages.create(from_=TWILIO_PHONE_NUMBER, to=to, body=body)


def send_text_reminder(to, medicine):
    send_text_message(to, 'Reminder: Time to take %s as scheduled.' % medicine)
