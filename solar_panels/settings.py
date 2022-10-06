"""
Django settings for solar_panels project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import datetime
import os
from datetime import timedelta
from pathlib import Path

import django
import django_heroku
import environ
import dj_database_url
from django.utils.encoding import force_str, smart_str
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import gettext_lazy

django.utils.encoding.force_text = force_str
django.utils.translation.ugettext_lazy = gettext_lazy
django.utils.translation.ugettext = gettext_lazy
django.utils.encoding.python_2_unicode_compatible = python_2_unicode_compatible
django.utils.encoding.smart_text = smart_str


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*', 'sopanel.herokuapp.com', 'localhost', 'https://d416-212-47-136-101.eu.ngrok.io'] 

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'rest_auth',
    'knox',
    'django_countries',
    'djrichtextfield',
    'phonenumbers',
    'djmoney',

    'celery',
    'django_celery_beat',
    'django_celery_results',

    'rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'storages',

    'compressor',

    'allauth.socialaccount.providers.google',
    'geoip2',

    'user.apps.UserConfig',
    'main.apps.MainConfig',
    'product.apps.ProductConfig',
    'cart.apps.CartConfig',
    'order.apps.OrderConfig',
    'quoute_builder.apps.QuouteBuilderConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = 'solar_panels.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.geoip', 
                'main.context_processors.cart_items'
            ],
        },
    },
]

WSGI_APPLICATION = 'solar_panels.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {}

if os.environ['DEBUG'] == 'False':
    DATABASES['default'] =  dj_database_url.config(default='postgresql://postgres:apple_2001@database-1.cmxyn388s7si.us-east-1.rds.amazonaws.com:5432/database1?sslrootcert=global-bundle.pem&sslmode=require', conn_max_age=600)
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASSWORD'],
            'HOST': os.environ['DB_HOST'],
            'PORT': os.environ['DB_PORT'],
        }
    }


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'mysite.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'MYAPP': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

DEBUG_PROPAGATE_EXCEPTIONS = True

DJRICHTEXTFIELD_CONFIG = {
    'js': ['//cdn.tiny.cloud/1/no-api-key/tinymce/5/tinymce.min.js'],
    'init_template': 'djrichtextfield/init/tinymce.js',
    'settings': {
        'menubar': False,
        'plugins': 'link image',
        'toolbar': 'bold italic | link image | removeformat',
        'width': 700
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        #'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    "EXCEPTION_HANDLER": "main.utils.api_exception_handler",
}

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True

AUTHENTICATION_BACKENDS = (
    # username login
    'django.contrib.auth.backends.ModelBackend',
    # email login
    "user.auth_backends.EmailBackend",
)

ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 7
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    """
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },"""
]


SITE_ID = 1

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "key": ""
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        }
    }
}

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']

BROKER_URL = os.environ['REDIS_URL']
BACKEND_URL = os.environ['REDIS_URL']
CELERY_RESULT_BACKEND = os.environ['REDIS_URL']
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Baku' 

STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET']
STRIPE_WEBHOOK_SECRET = os.environ['STRIPE_WEBHOOK_SECRET']
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    #'social_core.backends.google.GoogleOAuth2',
]

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':'rest_framework_jwt.utils.jwt_encode_handler',
    'JWT_DECODE_HANDLER':'rest_framework_jwt.utils.jwt_decode_handler',
    'JWT_PAYLOAD_HANDLER':'rest_framework_jwt.utils.jwt_payload_handler',
    'JWT_PAYLOAD_GET_USER_ID_HANDLER':'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER':'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=1),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,
    
}

REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'user.serializers.LoginSerializer',
    'USER_DETAILS_SERIALIZER': 'user.serializers.UserSerializer',
}

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'user.serializers.CustomRegisterSerializer'
}

REST_USE_JWT = True

# GEOLOCAITON CONFIGS
GEOIP_PATH =os.path.join('geoip')

SESSION_COOKIE_SECURE = False

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_CLOUDFRONT_DOMAIN = os.environ['AWS_CLOUDFRONT_DOMAIN']
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

AWS_QUERYSTRING_AUTH = False

# Only public read for now
AWS_QUERYSTRING_AUTH = False

AWS_S3_FILE_OVERWRITE = False

MEDIAFILES_LOCATION = ''
MEDIA_ROOT = '/%s/' % MEDIAFILES_LOCATION
MEDIA_URL = '//%s/' % (AWS_CLOUDFRONT_DOMAIN)

DEFAULT_FILE_STORAGE = 'solar_panels.storage_backends.MediaStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

def get_cache():
    import os
    try:
        servers = os.environ['MEMCACHEDCLOUD_SERVERS']
        username = os.environ['MEMCACHEDCLOUD_USERNAME']
        password = os.environ['MEMCACHEDCLOUD_PASSWORD']

        return {
            'default': {
                'BACKEND': 'django_bmemcached.memcached.BMemcached',
                'TIMEOUT': None,
                'LOCATION': servers,
                'OPTIONS': {
                    'username': username,
                    'password': password,
                }
            },
        }
    except:
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'BINARY': True,
                'LOCATION': '127.0.0.1.11211',
            },
        }

CACHES = get_cache()

COMPRESS_ENABLED = True
COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_FILTERS = {
    'css':[
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.rCSSMinFilter',
    ],
    'js':[
        'compressor.filters.jsmin.JSMinFilter',
    ]
}
HTML_MINIFY = True
KEEP_COMMENTS_ON_MINIFYING = True

django_heroku.settings(locals())
