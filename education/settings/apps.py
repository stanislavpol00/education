from .base import DEBUG

PRE_EXTERNAL_APPS = [
    "dal",
    "dal_select2",
]

DJANGO_APPs = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

POST_EXTERNAL_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "storages",
    "corsheaders",
    "django_extensions",
    "django_celery_beat",
    "django_celery_results",
    "django_filters",
    "reversion",
    "reversion_compare",
    "notifications",
    "import_export",
    "channels",
    "taggit",
    "rangefilter",
    "django_admin_multiple_choice_list_filter",
    "django_rest_passwordreset",
]
INTERNAL_APPS = [
    "main",
]

INSTALLED_APPS = (
    PRE_EXTERNAL_APPS + DJANGO_APPs + POST_EXTERNAL_APPS + INTERNAL_APPS
)

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
