"""
Django settings for monolithic_api project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os

from pathlib import Path

from datetime import timedelta

from decouple import config

from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", config("SECRET_KEY"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", config("DEBUG", cast=bool))

ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", config("ALLOWED_HOSTS"))]

USER_URL = os.environ.get("USER_URL", config("USER_URL"))

SITE_NAME = os.environ.get("SITE_NAME", config("SITE_NAME"))


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "django_celery_results",
    "storages",
    "drf_yasg",
    "rest_framework",
    "corsheaders",
    "django_filters",
    "api_admin.apps.ApiAdminConfig",
    "upload.apps.UploadConfig",
    "user.apps.UserConfig",
    "referral.apps.ReferralConfig",
    "account.apps.AccountConfig",
    "bank.apps.BankConfig",
    "blockchain.apps.BlockchainConfig",
    "transaction.apps.TransactionConfig",
    "withdrawal.apps.WithdrawalConfig",
    "term.apps.TermConfig",
    "stake.apps.StakeConfig",
    "contract.apps.ContractConfig",
    "invest.apps.InvestConfig",
    "goldmine.apps.GoldmineConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "monolithic_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "monolithic_api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": os.environ.get("DB_HOST", config("DB_HOST")),
        "PORT": os.environ.get("DB_PORT", config("DB_PORT")),
        "USER": os.environ.get("DB_USER", config("DB_USER")),
        "PASSWORD": os.environ.get("DB_PASSWORD", config("DB_PASSWORD")),
        "NAME": os.environ.get("DB_NAME", config("DB_NAME")),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
]


# Substituting a custom User model

AUTH_USER_MODEL = "user.User"


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Email settings

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", config("EMAIL_HOST"))
EMAIL_PORT = os.environ.get("EMAIL_PORT", config("EMAIL_PORT"))
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", config("EMAIL_USE_SSL", cast=bool))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", config("EMAIL_HOST_USER"))
EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD", config("EMAIL_HOST_PASSWORD")
)
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", config("EMAIL_SENDER"))


# Django REST framework
# https://www.django-rest-framework.org/#installation

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}


# Simple JWT Settings
# https://github.com/davesque/django-rest-framework-simplejwt

SIMPLE_JWT = {
    # ACCESS_TOKEN_LIFETIME by Mintue
    "ACCESS_TOKEN_LIFETIME": timedelta(
        days=os.environ.get("ACCESS_TOKEN_LIFETIME", 30)
    ),
    # REFRESH_TOKEN_LIFETIME by Day
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=os.environ.get("REFRESH_TOKEN_LIFETIME", 60)
    ),
}


# django-cors-headers
# https://github.com/adamchainz/django-cors-headers

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "https://admin.capitalfin.co.uk,https://member.capitalfin.co.uk",
).split(",")

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


# AWS storage settings

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", config("AWS_ACCESS_KEY_ID"))
AWS_SECRET_ACCESS_KEY = os.environ.get(
    "AWS_SECRET_ACCESS_KEY", config("AWS_SECRET_ACCESS_KEY")
)
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", config("AWS_S3_REGION_NAME"))
AWS_S3_ENDPOINT_URL = os.environ.get(
    "AWS_S3_ENDPOINT_URL", config("AWS_S3_ENDPOINT_URL")
)
AWS_STORAGE_BUCKET_NAME = os.environ.get(
    "AWS_STORAGE_BUCKET_NAME", config("AWS_STORAGE_BUCKET_NAME")
)
DEFAULT_FILE_STORAGE = "monolithic_api.storages.MediaStorage"
FILE_UPLOAD_PERMISSIONS = 0o644


# Celery avaliable config settings
# https://docs.celeryproject.org/en/stable/userguide/configuration.html

CELERY_APP = os.environ.get("CELERY_APP", config("CELERY_APP"))
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", config("CELERY_BROKER_URL"))
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_BEAT_SCHEDULE = {
    "daily_process": {
        "task": "daily_process",
        "schedule": crontab(minute=1, hour="0"),
    },
    "monthly_process": {
        "task": "monthly_process",
        "schedule": crontab(minute=0, hour="4", day_of_month="1"),
    },
}
