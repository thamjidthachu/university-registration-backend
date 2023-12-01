import random

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from sms.smsSend import SmsSend

import logging
logger_email = logging.getLogger("email")


class VerifyPhone(GenericAPIView):

    def post(self, request, *args, **kwargs):
        email = None
        code = str(random.randint(1000, 9999))
        phone = str(self.request.data.get('phone', None))
        email = str(self.request.data.get('email', None))
        message = "Your verification code: " + code + ", For registration in ALMAAREFA UNIVERSITY."
        try:
            if phone != 'None':
                SmsSend().sendSingleNumber(phone, message)
            else:
                logger_email.debug(f'Sending Email to >>>> {email}')
                logger_email.debug(f"Subject: `{'Al Maarefa University - Verification Code - ' + code}`")
                logger_email.debug(f"Message: `{message}`")
                send_mail(
                    subject='Al Maarefa University - Verification Code - ' + code,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False
                )
                logger_email.debug(f'Send Email >>>> Done')
            return Response({"code": code}, status=HTTP_200_OK)
        except Exception as e:
            logger_email.debug(f'Error in send email or sms {str(e)}')
            return Response(
                {"ERROR": "invalid Phone Number or Email", "ERROR_ar": "رقم الهاتف أو البريد الإلكتروني غير صالح"},
                status=HTTP_400_BAD_REQUEST)
