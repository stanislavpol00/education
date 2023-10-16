from .base import BASE_DIR

LOG_DIRECTORY = BASE_DIR
LOG_LEVEL = "DEBUG"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
        "default": {
            "format": "%(asctime)s %(name)s %(levelname)s %(pathname)s:%(lineno)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}
