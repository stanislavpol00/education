from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class NotificationWebsocketMixin:
    @classmethod
    def prepare_data(cls):
        return {"new_notification": True}

    @classmethod
    def send_new_notification_to_websocket(cls, user_id):
        data = cls.prepare_data()

        channel_layer = get_channel_layer()

        group_name = "user_{}".format(user_id)

        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "send_message", "data": data}
        )
