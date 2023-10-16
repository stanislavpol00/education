import datetime

from .base import env

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # "PAGE_SIZE": 100,
    # throttle
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/minute", "user": "1000/minute"},
    # filter
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
}

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "v1.serializers.UserAuthSerializer",
    "JWT_SERIALIZER": "libs.jwt_auth.custom_jwt_serializer.CustomJWTSerializer",
}
OLD_PASSWORD_FIELD_ENABLED = True

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("JWT",),
}

REST_USE_JWT = True

# Custom for temporary login
TEMPORARY_JWT_EXPIRATION_DELTA = datetime.timedelta(
    days=env.int("TEMPORARY_JWT_DAYS", default=10)
)
