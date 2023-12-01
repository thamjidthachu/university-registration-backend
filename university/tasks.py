from celery import shared_task
from sms import SmsSend


@shared_task
def balance_status():
    SmsSend().balance()
