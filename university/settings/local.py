from .base import *

STATIC_URL = '/static/'

USE_X_FORWARDED_HOST = None
FORCE_SCRIPT_NAME = None
ORACLE = 'MCSTTEST'
# ADMINS = ()
LOGGING = None
DOMAIN_URL = "/portal"

# test payment config
VISA_ENTITY_ID = "8a8294174b7ecb28014b9699220015ca"
MADA_ENTITY_ID = "8a8294174b7ecb28014b9699220015ca"
PAYMENT_SECRET_KEY = "OGE4Mjk0MTc0YjdlY2IyODAxNGI5Njk5MjIwMDE1Y2N8c3k2S0pzVDg="
PAYMENT_BASE_URL = "https://eu-test.oppwa.com"