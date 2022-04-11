import os

from . import *  # noqa: F403

ALLOWED_HOSTS = ['*']

SITE_ID = 1

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'USER': 'postgres',
        'NAME': 'database',
        'PASSWORD': 'password',
        'PORT': '',
    }
}

# Core Web DB
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'HOST': '10.31.246.70',
#         'NAME': 'cogi_core',
#         'PASSWORD': '',
#         'PORT': '',
#     }
# }

STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # noqa: F405

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

MICROSERVICE_API_OVERRIDE_KEY = os.environ.get("MICROSERVICE_API_OVERRIDE_KEY", "")

# JWT Parsing
JWT_ALGORITHMS = os.environ.get("JWT_ALGORITHMS", "").split(',')
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "")
JWT_SECRET = os.environ.get("JWT_SECRET", "")

# add the correct application credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/google-cloud.json"

# define the default file storage for both static and media
DEFAULT_FILE_STORAGE = 'service.storage_backends.GoogleCloudMediaStorage'
STATICFILES_STORAGE = 'service.storage_backends.GoogleCloudStaticStorage'

# add the names of the buckets
GS_MEDIA_BUCKET_NAME = 'cirrus-media-assets'
GS_STATIC_BUCKET_NAME = 'cirrus-static-assets'

# define the static urls for both static and media
STATIC_URL = 'https://storage.googleapis.com/{}/'.format(GS_STATIC_BUCKET_NAME)
MEDIA_URL = 'https://storage.googleapis.com/{}/'.format(GS_MEDIA_BUCKET_NAME)

SOCIALACCOUNT_PROVIDERS = {
    'auth0': {
        'AUTH0_URL': 'https://mydomain.auth0.com',
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
            'youtube',
            'youtube.force-ssl',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        }
    }
}

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
import os
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")

import base64
ZOOM_CLIENT_ID = os.environ.get('ZOOM_CLIENT_ID', 'nI4lCUeRXOGrbhZveLaw')
ZOOM_CLIENT_SECRET = os.environ.get('ZOOM_CLIENT_SECRET', '')
ZOOM_AUTH_STR = bytes("{}:{}".format(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET), "utf-8")
ZOOM_AUTHORIZATION = ''
ZOOM_DOMAIN = os.environ.get('ZOOM_DOMAIN', 'https://sub.mydomain.com')

LOGIN_URL = '/accounts/auth0/login'


"106590582104-io066o1ge0esinpbneh27qh1f6l1a6nb.apps.googleusercontent.com"
# GOOGLE_OAUTH2_CLIENT_ID = YOUTUBE_CLIENT_ID = '106590582104-io066o1ge0esinpbneh27qh1f6l1a6nb.apps.googleusercontent.com'
# GOOGLE_OAUTH2_CLIENT_SECRET = YOUTUBE_CLIENT_SECRET = '8kKGE7HbZNI0VEkzKUAguBgq'

GOOGLE_OAUTH2_CLIENT_ID="276329493925-g24s186ta12avidcqhmtuvqgq9ifad8l.apps.googleusercontent.com"
GOOGLE_OAUTH2_CLIENT_SECRET="ImqKR2uB10Qp-eweKlcbR20n"

# YOUTUBE_REDIRECT_URI = 'https://{}/integration/google/oauth2callback'.format(ROOT_URLS['portfolio'][
#                                                                                  DEPLOYMENT_NAME])

# GOOGLE_OAUTH2_CLIENT_ID = "106590582104-io066o1ge0esinpbneh27qh1f6l1a6nb.apps.googleusercontent.com"
# GOOGLE_OAUTH2_CLIENT_SECRET = '<Your Client Secret from Google Developer Console>'
# GOOGLE_OAUTH2_CALLBACK_VIEW = 'oauth2callback'  # your oauth callback view name

import analytics

analytics.write_key = 'ztjlvo2JF88XlFEhpBvM7LqfW8PxJcRE'

SECRET_KEY = 'p3223i2j2i3f23fj23fi23ufni2f232'

ACCOUNT_LOGOUT_ON_GET = True
LOGIN_REDIRECT_URL = '/library'
LOGOUT_REDIRECT_URL = '/'

GOOGLE_OAUTH2_CLIENT_SECRETS_JSON = "client_secrets.json"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://e7d8e071eaf348ab9b52600d21b83859@sentry.mydomain.co/7",
    integrations=[DjangoIntegration()]
)
NEW_ORDER_TOPIC = os.environ.get('NEW_ORDER_TOPIC', '') 


# ===============================================================================
# SendGrid credentials
# ===============================================================================
SENDGRID_API_KEY = ''

ZOOM_REDIRECT_URI = "https://sub.mydomain.com/integrations/zoom/oauth"

from datetime import datetime, timedelta

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': "",
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': "",
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': timedelta(seconds=900),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': "https://auth.mydomain.com",

    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,

}