from pathlib import Path
from django.utils.translation import gettext_lazy as _
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# Добавляем папку apps в системные пути
sys.path.insert(0, str(BASE_DIR / 'apps'))


""" Application definition """
from .conf import SECRET_KEY

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_spectacular',
    # my project
    'apps.blog',
    'apps.users',
    'apps.core',
    'apps.stats',
    'apps.notifications',
    'channels',
]


""" Middleware """

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', # base
    'django.contrib.sessions.middleware.SessionMiddleware', # base
    'django.middleware.common.CommonMiddleware', # base
    'django.middleware.csrf.CsrfViewMiddleware', # base
    'django.contrib.auth.middleware.AuthenticationMiddleware', # base
    'django.contrib.messages.middleware.MessageMiddleware', # base
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # base
    'django.middleware.locale.LocaleMiddleware', # I added
    'apps.core.middleware.LanguageMiddleware', # I added
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'
ASGI_APPLICATION = 'settings.asgi.application'

AUTH_USER_MODEL = "users.User"


""" Database """

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


""" Password validation """

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


""" I18N """

LANGUAGE_CODE = 'en'
LANGUAGES= [
    ('en', _('English')),
    ('ru', _('Russian')),
    ('kk', _('Kazakh')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


""" Static files """

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


""" DRF """

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


""" DRF-Spectacular """

SPECTACULAR_SETTINGS = {
    'TITLE': 'Blog Api',
    'DESCRIPTION': 'Multilanguage blog API with async stats endpoint.',
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'TAGS': [
        {'name': 'Auth', 'description': 'Registration and JWT tokens'},
        {'name': 'Posts', 'description': 'Blog posts CRUD'},
        {'name': 'Comments', 'description': 'Post comments'},
        {'name': 'Stats', 'description': 'Blog statistics with external data'},
    ],
}


""" Redis cache """

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

REDIS_URL = 'redis://127.0.0.1:6379/0'


""" Logger """

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} |{name:36s}|:{lineno:<4d}"
            "[{levelname:8s}] <{request_id:36s}> - {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname:8s}] - {message}",
            "style": "{",
        },
        "django_request": {
            "format": "{asctime} [{levelname:8s}] <{request_id:36s}> - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "warning_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(BASE_DIR / "logs" / "app.log"),
            "formatter": "verbose",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
        },
        "debug_requests": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(BASE_DIR / "logs" / "debug_requests.log"),
            "formatter": "verbose",
            "maxBytes": 50 * 1024 * 1024,
            "backupCount": 5,
        },
    },
    "loggers": {
        "users": {
            "handlers": ["console", "warning_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "blog": {
            "handlers": ["console", "warning_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "stats": {
            "handlers": ["warning_file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
""" Celery """
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'publish_scheduled_posts': {
        'task': 'apps.blog.tasks.publish_scheduled_posts',
        'schedule': crontab(minute='*/5'),
    },
    'clear_expired_notifications': {
        'task': 'apps.notifications.tasks.clear_expired_notifications',
        'schedule': crontab(hour=0, minute=0), # Daily at midnight
    },
}
