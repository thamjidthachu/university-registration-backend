from .base import *

DEBUG = int(config("DEBUG"))

ALLOWED_HOSTS = ['my.um.edu.sa', 'uat.um.edu.sa', 'dev.um.edu.sa', 'localhost:9003']
STATIC_URL = '/registration/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = []

STATIC_ROOT = BASE_DIR / "static"
USE_X_FORWARDED_HOST = True
FORCE_SCRIPT_NAME = "/backend"
REDIRECT_URL = "/portal"
DOMAIN_URL = "/portal"

CELERY_BROKER_URL = 'redis://redis:6379/4'

ORACLE = config("ORACLE_VIEW")

URL_SERVER = "https://my.um.edu.sa/portal/"
