from django.urls import re_path

from .consumers import MainConsumer

websocket_urlpatterns = [
    re_path(r"^ws/", MainConsumer.as_asgi()),
]
