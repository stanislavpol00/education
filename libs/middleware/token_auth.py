from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.state import token_backend

from libs.jwt_auth.custom_jwt_payload_handler import get_username_field


@database_sync_to_async
def get_user(token_key):
    from django.contrib.auth.models import AnonymousUser

    from main.models import User

    username_field = get_username_field()

    try:
        payload = token_backend.decode(token_key)
        username = payload[username_field]
        return get_object_or_404(User, username=username)
    except Exception:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser

        query_params = parse_qs(scope["query_string"].decode())

        token_key = None
        if "token" in query_params:
            token_key = query_params.get("token")[0]

        scope["user"] = (
            AnonymousUser() if token_key is None else await get_user(token_key)
        )
        return await super().__call__(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(
    AuthMiddlewareStack(inner)
)
