import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class MainConsumer(WebsocketConsumer):
    def connect(self):
        if self.user.is_anonymous:
            self.close(code=401)
            return

        self.group_name = "user_{}".format(self.user.id)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

    @property
    def user(self):
        return self.scope["user"]

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        pass

    # Receive message from room group
    def send_message(self, event):
        data = event["data"]
        # Send message to WebSocket
        self.send(text_data=json.dumps(data))
