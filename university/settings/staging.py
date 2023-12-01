from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost:3000', '37.76.245.93', '127.0.0.1', 'dev.um.edu.sa']

DATABASES['default']['NAME'] = 'university_stage'

STATIC_URL = '/static/'

DOMAIN_URL = "/portal"

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/4'
MEDIA_URL = '/media/'
STATICFILES_DIRS = []

STATIC_ROOT = BASE_DIR / "static"


ORACLE = 'MCSTTEST'
