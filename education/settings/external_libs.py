import sys

from .base import env

# Sentry -
SENTRY_DSN = env.str("SENTRY_DSN", default="")
if SENTRY_DSN and sys.argv[1] != "test":
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )

# Debug tool bar - https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
INTERNAL_IPS = ["127.0.0.1"]

# aws
USE_S3 = env.bool("USE_S3", default=False)
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", default="")

if USE_S3:
    AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
    STATICFILES_STORAGE = "libs.custom_storages.StaticStorage"
    DEFAULT_FILE_STORAGE = "libs.custom_storages.MediaStorage"
