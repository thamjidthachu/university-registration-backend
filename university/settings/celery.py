import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university.settings.develop')


app = Celery('university')

app.config_from_object('django.conf:settings', namespace="CELERY")


app.conf.beat_schedule = {
    "studentId-every-5min": {
        'task': 'registration.tasks.get_student_id',
        'schedule': crontab(minute='*/5'),

    },
    "Eregister-process-every-1min": {
        'task': 'registration.tasks.start_oracle_process',
        'schedule': crontab(minute='*/1'),
    },

    "Eregister-major-process-every-1min": {
        'task': 'registration.tasks.start_oracle_major_process',
        'schedule': crontab(minute='*/1'),
    },

    # "Eregister-pay-process-every-1min": {
    #     'task': 'registration.tasks.start_oracle_pay_process',
    #     'schedule': crontab(minute='*/1'),
    # },

    "Sms-Balance-Status-every-day": {
        'task': 'registration.tasks.balance_status',
        'schedule': crontab(minute='*/1'),
    }
}

app.autodiscover_tasks()
