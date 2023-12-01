from celery import shared_task
from email_handling.views.email_send import Mail
from .scripts.studentId import getStudentID
from .scripts.oracleProcess import store_oracle_process, payment_oracle_process, start_process, start_payment_process, \
    start_major_process
from django.conf import settings
import logging
from equations.models.equations import Equation
from sms import SmsSend

logger = logging.getLogger("root")
logger_email = logging.getLogger("email")


@shared_task
def send_email(domain, name, email, arabic_name=None, gender=None, url=None, *args, **kwargs):
    try:
        logger_email.debug(f'Sending Email to >>>> {email}')
        logger_email.debug(f"Subject: `{kwargs['subject']}")
        logger_email.debug(f"Message: `{kwargs['english']}`")
        Mail(domain, name, email, arabic_name, gender, link=url).send(*args, **kwargs)
        logger_email.debug(f'Send Email >>>> Done')
    except Exception as e:
        logger_email.error(f'Error in send email {str(e)}')

    return


@shared_task
def get_student_id():
    try:
        ids_applicants = getStudentID()
        from email_handling.views.body_mails import StudentIDMail, StudentIDNotFreshMail

        for app in ids_applicants:

            if app.applicant_type == 'FS':
                body = StudentIDMail(app)

            else:
                applicant_equation = Equation.objects.filter(applicant=app)
                if not applicant_equation.exists():
                    body = StudentIDNotFreshMail(app)
                else:
                    body = StudentIDMail(app)
            if app.accepted_outside:
                send_email(settings.URL_SERVER, app.first_name, app.email, app.arabic_first_name, app.gender,
                           english=body['english'], arabic=body['arabic'],
                           subject='Al Maarefa University KSA Received Student ID',
                           link="Go to Dashboard", file='outside')
            else:
                send_email(settings.URL_SERVER, app.first_name, app.email, app.arabic_first_name, app.gender,
                           english=body['english'], arabic=body['arabic'],
                           subject='Al Maarefa University KSA Received Student ID', link="Go to Dashboard")

    except Exception as e:
        logger.error(f'error in task student id {str(e)}')

    return


@shared_task
def saved_oracle_process(id, email, national_id, process):
    store = store_oracle_process(id, email, national_id, process)

    if not isinstance(store, bool):
        logger.error(store)


@shared_task
def save_payment_oracle_process(applicant_id, payment, process):
    store = payment_oracle_process(applicant_id, payment, process)

    if not isinstance(store, bool):
        logger.error(store)


@shared_task
def start_oracle_process():
    start = start_process()
    if not isinstance(start, bool):
        logger.error(start)


@shared_task
def start_oracle_major_process():
    start = start_major_process()
    if not isinstance(start, bool):
        logger.error(start)


@shared_task
def start_oracle_pay_process():
    start = start_payment_process()
    if not isinstance(start, bool):
        logger.error(start)


@shared_task
def balance_status():
    SmsSend().balance()
