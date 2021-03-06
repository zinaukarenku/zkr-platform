"""
Django settings for zkr project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import logging.config
from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
if 'DEV' in os.environ:
    CELERY_TASK_ALWAYS_EAGER = True  # Sync celery tasks in sync
    DEBUG = True

ENABLE_DEBUG_DRAWER_IN_DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY') if not DEBUG else 'DEBUG'

GIT_COMMIT = 'DEBUG' if DEBUG else os.environ.get('GIT_COMMIT')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',') if not DEBUG else []

INTERNAL_IPS = ['127.0.0.1']

USE_X_FORWARDED_HOST = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.postgres',
    

    'raven.contrib.django.raven_compat',
    'ddtrace.contrib.django',

    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'drf_yasg',
    'rest_framework_tracking',

    'crispy_forms',
    'django_celery_results',
    'adminsortable2',
    'reversion',
    'snowpenguin.django.recaptcha3',

    'utils',
    'seimas',
    'elections',
    'web',
    'questions',
    'api',
    'politicians',
    'nested_inline',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware'
]

AUTH_USER_MODEL = 'web.User'

if DEBUG and ENABLE_DEBUG_DRAWER_IN_DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    MIDDLEWARE.append('zkr.middleware.NonHtmlDebugToolbarMiddleware')
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

ROOT_URLCONF = 'zkr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'zkr.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
IS_POSTGRES_AVAILABLE = 'POSTGRES_DB' in os.environ and 'POSTGRES_USER' in os.environ and 'POSTGRES_PASSWORD' in os.environ and 'POSTGRES_HOST' in os.environ

if DEBUG and not IS_POSTGRES_AVAILABLE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': '5432',
        }
    }

SENTRY_KEY = os.environ.get("SENTRY_KEY", None)
SENTRY_SECRET = os.environ.get("SENTRY_SECRET", None)
SENTRY_PROJECT_ID = os.environ.get("SENTRY_PROJECT_ID", None)
RAVEN_CONFIG = None
if SENTRY_KEY and SENTRY_SECRET and SENTRY_PROJECT_ID:
    RAVEN_CONFIG = {
        'dsn': f'https://{SENTRY_KEY}:{SENTRY_SECRET}@sentry.io/{SENTRY_PROJECT_ID}',
        'release': GIT_COMMIT,
        'ignore_exceptions': [
            'UnicodeDecodeError',
        ]
    }

# https://lincolnloop.com/blog/django-logging-right-way/
# Disable Django's logging setup
LOGGING_CONFIG = None
LOGGER_HANDLERS = ['console'] if RAVEN_CONFIG else ['console', 'sentry']
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)-12s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  # STDERR
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        '': {
            'level': 'WARNING',
            'handlers': LOGGER_HANDLERS,
        },
        'web': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        'seimas': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        'elections': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        'questions': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        'utils': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        'api': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'lt'

TIME_ZONE = 'Europe/Vilnius'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

SITE_ID = 1

# By default Django will upload to media with original file permissions. Fix this.
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

REDIS_URL = 'redis://%s:6379/' % os.environ.get('REDIS_PORT_6379_TCP_ADDR', '172.17.0.1')

CELERY_BROKER_URL = REDIS_URL + '2'
CELERY_RESULT_BACKEND = 'django-db'

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

CELERY_BEAT_SCHEDULE = {
    'sync_politician_information': {
        'task': 'web.tasks.sync_politician_information',
        'schedule': crontab(minute='*/5', hour='*')
    },
    # 'fetch_politicians': {
    #     'task': 'seimas.tasks.fetch_politicians',
    #     'schedule': crontab(minute='0', hour='*')
    # },
    # 'fetch_and_match_fractions_with_politicians': {
    #     'task': 'seimas.tasks.fetch_and_match_fractions_with_politicians',
    #     'schedule': crontab(minute='10', hour='*')
    # },
    # 'fetch_and_match_committees_with_politicians': {
    #     'task': 'seimas.tasks.fetch_and_match_committees_with_politicians',
    #     'schedule': crontab(minute='15', hour='*')
    # },
    # 'fetch_and_match_commissions_with_politicians': {
    #     'task': 'seimas.tasks.fetch_and_match_commissions_with_politicians',
    #     'schedule': crontab(minute='20', hour='*')
    # },
    # 'fetch_terms': {
    #     'task': 'seimas.tasks.fetch_terms',
    #     'schedule': crontab(minute='30', hour='11')
    # },
    # 'fetch_sessions': {
    #     'task': 'seimas.tasks.fetch_sessions',
    #     'schedule': crontab(minute='30', hour='12')
    # },
    # 'fetch_and_match_sessions_with_politicians': {
    #     'task': 'seimas.tasks.fetch_and_match_sessions_with_politicians',
    #     'schedule': crontab(minute='50', hour='12')
    # },
    # 'fetch_business_trips': {
    #     'task': 'seimas.tasks.fetch_business_trips',
    #     'schedule': crontab(minute='20', hour='*')
    # },
    # 'fetch_politician_documents': {
    #     'task': 'seimas.tasks.fetch_politician_documents',
    #     'schedule': crontab(minute='30', hour='*')
    # },
    # 'fetch_vrk_elections': {
    #     'task': 'elections.tasks.fetch_vrk_elections',
    #     'schedule': crontab(minute='30', hour='*')
    # },
    # 'fetch_vrk_election_results': {
    #     'task': 'elections.tasks.fetch_vrk_election_results',
    #     'schedule': crontab(minute='*/5', hour='*')
    # },
    # 'sync_newsletter_subscribers': {
    #     'task': 'web.tasks.sync_newsletter_subscribers',
    #     'schedule': crontab(minute='*/15', hour='*')
    # },
    # 'sync_seimas_with_sendgrid': {
    #     'task': 'seimas.tasks.sync_seimas_with_sendgrid',
    #     'schedule': crontab(minute='10', hour='*')
    # },
    # 'fetch_president_articles': {
    #     'task': 'elections.tasks.fetch_president_articles',
    #     'schedule': crontab(minute='*/30', hour='*')
    # },
}

CELERYD_TASK_SOFT_TIME_LIMIT = 45 * 60
CELERYD_SEND_EVENTS = True

CELERY_TASK_SEND_SENT_EVENT = True
CELERY_TRACK_STARTED = True

if not DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

DJANGORESIZED_DEFAULT_QUALITY = 90
DJANGORESIZED_DEFAULT_KEEP_META = False
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Authentication
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
LOGIN_REDIRECT_URL = "user_profile"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_FORMS = {
    'login': 'web.forms.LoginForm',
    'signup': 'web.forms.SignupForm',
    'reset_password': 'web.forms.ResetPasswordForm',
}
SOCIALACCOUNT_FORMS = {
    'signup': 'web.forms.SocialSignupForm',
}
ACCOUNT_ADAPTER = 'web.adapters.AccountAdapter'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# Recaptcha

if DEBUG:
    os.environ['RECAPTCHA_DISABLE'] = 'True'

RECAPTCHA_PUBLIC_KEY = \
    os.environ.get('RECAPTCHA_PUBLIC_KEY') if not DEBUG else '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY = \
    os.environ.get('RECAPTCHA_PRIVATE_KEY') if not DEBUG else '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
RECAPTCHA_DEFAULT_ACTION = 'generic'

# Email and SendGrid
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', None)

DEFAULT_FROM_EMAIL = "info@zinaukarenku.lt"
EMAIL_FROM = DEFAULT_FROM_EMAIL
EMAIL_TO = [EMAIL_FROM, ]
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'

# Rest framework
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 30,
    'DATETIME_FORMAT': "%Y-%m-%dT%H:%M:%SZ",
}

# Datadog agent
DATADOG_TRACE = {
    'DEFAULT_SERVICE': 'zkr-platform',
    'AGENT_HOSTNAME': 'ddagent',
    'TAGS': {'env': 'production'},
}

# Other general settings

BASE_DOMAIN = "https://www.zinaukarenku.lt/" if not DEBUG else "http://localhost:8000/"

DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400
