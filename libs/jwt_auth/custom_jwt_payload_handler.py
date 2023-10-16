from calendar import timegm
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.settings import api_settings


def get_username_field():
    try:
        username_field = get_user_model().USERNAME_FIELD
    except Exception:
        username_field = "username"

    return username_field


def get_username(user):
    try:
        username = user.get_username()
    except AttributeError:
        username = user.username

    return username


def custom_jwt_payload_handler(user):
    username_field = get_username_field()
    username = get_username(user)

    payload = {
        "user_id": user.pk,
        "username": username,
        "exp": datetime.utcnow() + settings.TEMPORARY_JWT_EXPIRATION_DELTA,
    }
    if hasattr(user, "email"):
        payload["email"] = user.email

    payload[username_field] = username

    if api_settings.ROTATE_REFRESH_TOKENS:
        payload["orig_iat"] = timegm(datetime.utcnow().utctimetuple())

    # Temporary set token_type to access.
    # Should find other way to set properyly token_type.
    # Eg: access, or refresh
    payload[api_settings.TOKEN_TYPE_CLAIM] = "access"
    payload[api_settings.JTI_CLAIM] = None

    return payload
