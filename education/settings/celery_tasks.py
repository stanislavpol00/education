from .base import env
from .internationalization import TIME_ZONE

# Celery Configuration Options
# Celery
# -------------------------------------------------------------------------------
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
CELERY_BROKER_URL = env.cache_url(
    "CELERY_BROKER_URL", default="redis://localhost:6379/0"
)
CELERY_RESULT_BACKEND = env.cache_url(
    "CELERY_RESULT_BACKEND", default="redis://localhost:6379/0"
)
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ["pickle"]
CELERY_DEFAULT_QUEUE = "default"
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = env.bool(
    "CELERY_TASK_EAGER_PROPAGATES", default=False
)
