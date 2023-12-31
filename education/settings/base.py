"""
Django settings for education project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

import environ

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()

# common settings
DEBUG = env("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY", default="YOUR_SECRET_KEY")
ALLOWED_HOSTS = [
    "*"
]

ROOT_URLCONF = "education.urls"
WSGI_APPLICATION = "education.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# https://github.com/adamchainz/django-cors-headers
CORS_ALLOWED_ORIGINS = ["*"]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = False
default_headers = (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

AUTH_USER_MODEL = "main.User"

# Add me as admin (for the time being)
ADMINS = (("Ricardo Serrano", "rserrano@geomodelr.com"),)
MANAGERS = ADMINS

CRONTAB_COMMAND_SUFFIX = "2>&1"
# Cron job configuration
CRONJOBS = [
    ("*/1 * * * *", "main.crons.crons.read_student_email_and_create_episode"),
]

# https://github.com/jedie/django-reversion-compare
REVERSION_COMPARE_IGNORE_NOT_REGISTERED = True

# https://django-import-export.readthedocs.io/en/stable/installation.html#settings
IMPORT_EXPORT_USE_TRANSACTIONS = True


# https://django-taggit.readthedocs.io/en/latest/getting_started.html
TAGGIT_CASE_INSENSITIVE = True

# https://github.com/anexia-it/django-rest-passwordreset
DJANGO_REST_PASSWORDRESET_TOKEN_CONFIG = {
    "CLASS": "django_rest_passwordreset.tokens.RandomNumberTokenGenerator",
    "OPTIONS": {
        "min_number": 100000,
        "max_number": 999999,
    },
}

WEB_URL = env.str("WEB_URL", default="https://lsgrid.com/")

# AXES
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 20
