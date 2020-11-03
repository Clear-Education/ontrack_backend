"""
Django settings for ontrack project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import django_heroku


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "secret")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if os.getenv("SUPERADMIN"):
    DEVELOPER_ADMIN = True
else:
    DEVELOPER_ADMIN = False

SILENCED_SYSTEM_CHECKS = ["auth.E003", "auth.W004"]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ["*"]

DATE_INPUT_FORMAT = ["%d/%m/%Y"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Packages
    "rest_framework",
    "rest_framework.authtoken",
    "softdelete",
    "django_rest_passwordreset",
    "drf_yasg",
    "corsheaders",
    "django_rq",
    "storages",
    "dbbackup",
    # Custom
    "users",
    "instituciones",
    "curricula",
    "alumnos",
    "calificaciones",
    "asistencias",
    "seguimientos",
    "objetivos",
    "actualizaciones",
    "mantenimiento",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    "NON_FIELD_ERRORS_KEY": "detail",
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_LOCAL = {
    "HOST": "redis",
    "PORT": 6379,
    "DB": 0,
    "PASSWORD": "redis_ontrack",
    "DEFAULT_TIMEOUT": 500,
}

DEFAULT_HEROKU = {
    "URL": os.getenv("REDISTOGO_URL", "redis"),
    "DEFAULT_TIMEOUT": 500,
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": DEFAULT_HEROKU["URL"],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MAX_ENTRIES": 5000,
        },
    }
}

if os.getenv("HEROKU"):
    RQ_QUEUES = {
        "default": {"USE_REDIS_CACHE": "default",},
    }
else:
    RQ_QUEUES = {
        "default": DEFAULT_LOCAL,
    }

ROOT_URLCONF = "ontrack.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "users/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ontrack.context_processors.export_env_vars",
            ],
        },
    },
]

WSGI_APPLICATION = "ontrack.wsgi.application"


# Database


if os.getenv("DJANGO_DEVELOPMENT"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": 5432,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": 5432,
        }
    }

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Auth Token: Token YOUR_TOKEN": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    }
}

CRON_CLASSES = [
    "ontrack.cron.Backup",
]


if os.getenv("BACKUPDB"):
    DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DBBACKUP_STORAGE_OPTIONS = {
        "access_key": os.environ.get("AWS_ACCESS_KEY_ID"),
        "secret_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "bucket_name": os.environ.get("AWS_STORAGE_BUCKET_NAME"),
        "default_acl": os.environ.get("AWS_DEFAULT_ACL", None),
        "region_name": os.environ.get("AWS_S3_REGION_NAME"),
        "location": "backups/",
    }

DBBACKUP_CONNECTORS = {
    "default": {
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "CONNECTOR": "dbbackup.db.postgresql.PgDumpBinaryConnector",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"

MEDIA_URL = "/images/"


STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_ROOT = os.path.join(BASE_DIR, "static/images")


# S3 BUCKETS CONFIG
if os.getenv("HEROKU"):
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_ADDRESSING_STYLE = "virtual"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")

AUTH_USER_MODEL = "users.User"

# MAIL

EMAIL_HOST = os.environ.get("MAILGUN_SMTP_SERVER", "")
EMAIL_PORT = os.environ.get("MAILGUN_SMTP_PORT", "")
EMAIL_HOST_USER = os.environ.get("MAILGUN_SMTP_LOGIN", "")
EMAIL_HOST_PASSWORD = os.environ.get("MAILGUN_SMTP_PASSWORD", "")

django_heroku.settings(locals())
