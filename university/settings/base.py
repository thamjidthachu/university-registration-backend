from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
MODE = config("MODE")
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    # 'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'whitenoise',
    'tokens',

    # apps
    'equations',
    'registration',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'registration.middleware.authenticateMiddleware.authenticateMiddleware',

]

ROOT_URLCONF = 'university.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'email_handling/templates', BASE_DIR / 'error_handling/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'university.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        'HOST': config("DB_HOST"),
        'PORT': config("DB_PORT"),
    }
}
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = config('LANGUAGE_CODE')

TIME_ZONE = config('TIME_ZONE')

USE_I18N = config('USE_I18N')

USE_L10N = config('USE_L10N')

USE_TZ = config('USE_TZ')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CORS_ALLOWED_ORIGINS = [k for k in config('CORS_ALLOWED_ORIGINS').split(",") if k]
CORS_ALLOW_CREDENTIALS = bool(int(config('CORS_ALLOW_CREDENTIALS')))
CORS_REPLACE_HTTPS_REFERER = bool(int(config('CORS_REPLACE_HTTPS_REFERER')))

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'POST',
    'PUT',
    'PATCH',
]
CORS_ALLOW_HEADERS = [
    'auth-session',
    'content-type',
    'accept',
    'accept-encoding',
    'authorization',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'auth'
]
CORS_EXPOSE_HEADERS = [
    'auth-session',
]
AUTH_USER_MODEL = 'registration.User'

# config email
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_USE_SSL = bool(int(config('EMAIL_USE_SSL')))
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
EMAIL_PORT = int(config('EMAIL_PORT'))
SERVER_EMAIL = DEFAULT_FROM_EMAIL

ADMINS = (
)

# configrue pusher real time
PUSHER_ID = "1106644"
PUSHER_KEY = "bcf8e7abd0651cc4f023"
PUSHER_SECRET = "8995729836c3ddfb62e2"
PUSHER_CLUSTER = "eu"

# configure celery

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# configure sms
SMS_SECRET_KEY = config("SMS_SECRET_KEY")
SMS_BASE_URL = config("SMS_BASE_URL")

URL_SERVER = "http://37.76.245.93/portal/"

WEB_BASE_URL = "/portal"

VISA_ENTITY_ID = config("VISA_ENTITY_ID")
MADA_ENTITY_ID = config("MADA_ENTITY_ID")
PAYMENT_SECRET_KEY = config("PAYMENT_SECRET_KEY")
PAYMENT_BASE_URL = config("PAYMENT_BASE_URL")

ORACLE_URL = config("ORACLE_URL")

# logging configurations
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(filename)s %(funcName)s %(lineno)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        'registration': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': str(BASE_DIR / "logs/registration_logs.log")
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': str(BASE_DIR / "logs/system_logs.log")
        },
        'email_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': str(BASE_DIR / "logs/email_logs.log")
        },
        'payment_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': str(BASE_DIR / "logs/payment_logs.log")
        },
        'sms_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': str(BASE_DIR / "logs/sms_logs.log")
        },
        'oracle_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': str(BASE_DIR / "logs/oracle_log.log")
        },
        'oracle_payment_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': str(BASE_DIR / "logs/oracle_payments_log.log")
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    "loggers": {
        'root': {
            'level': "DEBUG",
            'handlers': ['file'],
            'propagate': True
        },
        'registration': {
            'level': "DEBUG",
            'handlers': ['registration'],
            'propagate': True
        },
        'email': {
            'level': "DEBUG",
            'handlers': ['email_file'],
            'propagate': True
        },
        'payment_logs': {
            'level': "DEBUG",
            'handlers': ['payment_file'],
            'propagate': True
        },
        'sms_logs': {
            'level': "DEBUG",
            'handlers': ['sms_file'],
            'propagate': True
        },
        'oracle_logs': {
            'level': "ERROR",
            'handlers': ['oracle_file'],
            'propagate': True
        },
        'oracle_payment_updates': {
            'level': "DEBUG",
            'handlers': ['oracle_payment_file'],
            'propagate': True
        },
        'django': {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": True
        },
        'django.request': {
            "handlers": ['mail_admins'],
            'propagate': False
        },
        'django.server': {
            "handlers": ['mail_admins'],
            'propagate': False
        },
        'oracle': {
            'level': "ERROR",
            "handlers": ['mail_admins'],
            'propagate': False
        }
    },
}

CURRENT_SEMESTER = config('CURRENT_SEMESTER')
