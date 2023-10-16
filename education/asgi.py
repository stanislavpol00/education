import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from websocket import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")
django_asgi_app = get_asgi_application()

from libs.middleware import TokenAuthMiddlewareStack

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": TokenAuthMiddlewareStack(
            URLRouter(routing.websocket_urlpatterns)
        ),
    }
)
