from .base import env

REDIS_CACHE_URL = env.cache(
    "REDIS_CACHE_URL", default="redis://127.0.0.1:6379/2"
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL["LOCATION"],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHE_ACCESS_LOG_MAX_COUNT = env.int(
    "CACHE_ACCESS_LOG_MAX_COUNT",
    default=10,
)
CACHE_ACCESS_LOG_MAX_DAYS = env.int(
    "CACHE_ACCESS_LOG_MAX_DAYS",
    default=1,
)
