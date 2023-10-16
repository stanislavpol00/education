import sys
import warnings

if sys.argv[1] == "test":
    warnings.simplefilter("ignore", category=RuntimeWarning)

    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
    RUNNING_MIGRATE_FLAG = True
    TEMPLATE_DEBUG = DEBUG = False

    ATOMIC_REQUESTS = False

    LOGGING_CONFIG = None
    CELERY_TASK_ALWAYS_EAGER = True
    LOG_LEVER = "ERROR"

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "cache_table",
        }
    }

    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

    AXES_ENABLED = False
