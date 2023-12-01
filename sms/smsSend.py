from rest_framework.exceptions import APIException
from django.core.mail import mail_admins
from datetime import datetime, timedelta
from django.conf import settings
import requests
import logging

logger = logging.getLogger("sms_logs")


class SmsSend:
    SMS_BASE_URL = settings.SMS_BASE_URL

    def sendSingleNumber(self, numbers, message):
        if not isinstance(numbers, list):
            numbers = [numbers]

        data = {
            "recipients": numbers,
            "body": message,
            "sender": "ALMAAREFA"
        }
        headers = {
            "Authorization": f"Bearer {settings.SMS_SECRET_KEY}"
        }

        try:
            response = requests.post(f"{self.SMS_BASE_URL}/v1/messages", data=data, headers=headers)

            result = response.json()
        except (requests.JSONDecodeError, requests.Timeout,
                requests.ConnectionError, requests.ReadTimeout,
                requests.ConnectTimeout) as e:

            logger.exception(f"[SMS-SEND-MSG] request error when send data {data} with error {str(e)}")
            raise APIException(detail="something went wrong please try again later")

        if 'statusCode' in result:
            if result.get("statusCode") == 201:
                return True
            logger.exception(f"[SMS-SEND-MSG] status code isn't 201 and result are {response.text}")
            raise APIException(detail=result.get("message"))

        error = {
            "error": "something went wrong, please try again",
            "error_ar": "حدث خطأ برجاء المحاولة مرة اخرة"
        }
        logger.exception(f"[SMS-SEND-MSG] error when get response send message {response.text}")
        mail_admins("Send Sms Message", message=f"Error when send data {data} and response is {response.text}")
        raise APIException(detail=error)

    def balance(self):
        headers = {
            "Authorization": f"Bearer {settings.SMS_SECRET_KEY}"
        }

        try:
            response = requests.get(f"{self.SMS_BASE_URL}/account/balance", headers=headers)

            result = response.json()

            if result['statusCode'] != 200:
                if "message" in result:
                    message = result['message']
                else:
                    message = str(response.text)

                logger.exception(
                    f"[SMS-STATUS-BALANCE-REQ-ERROR] request returned {result['statusCode']} with error {message}")
                mail_admins("Status Balance Request Error", message=message)
                return

            dt_now = (datetime.now() + timedelta(days=2)).date()

            if dt_now >= datetime.strptime(result['accountExpiryDate'], "%d-%m-%Y").date():
                mail_admins("Status Balance Expiry Date",
                            message=f"SMS provider will be expire after two days and the balance is {result['balance']} and message points are {result['points']}")

            if int(result['points']) <= 100:
                mail_admins("Status Balance Points",
                            message=f"The points for SMS provider are limited, we need to recharge the sms. the "
                                    f"number of message points are {result['points']}")

            return

        except (requests.JSONDecodeError, requests.Timeout,
                requests.ConnectionError, requests.ReadTimeout,
                requests.ConnectTimeout, Exception) as e:

            logger.exception(f"[SMS-STATUS-BALANCE] request error when get status balance error {str(e)}")
            mail_admins("Status Balance Error", message=result['message'])
            return
