from .base import *

ALLOWED_HOSTS = ['test', 'localhost']
TEMPLATES[0]['DIRS'].append(BASE_DIR / "frontend")

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "frontend/build/static"
]
STATIC_ROOT = BASE_DIR / "static"
USE_X_FORWARDED_HOST = True
FORCE_SCRIPT_NAME = "/test"
ORACLE = 'MCSTTEST'
