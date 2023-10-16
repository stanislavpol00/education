from .base import env

ASGI_APPLICATION = "education.asgi.application"

REDIS_CACHE_URL = env.cache(
    "REDIS_CACHE_URL", default="redis://127.0.0.1:6379/3"
)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_CACHE_URL["LOCATION"]],
        },
    },
}
