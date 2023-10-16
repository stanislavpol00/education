from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from notifications.models import Notification

import constants

from .notification_websocket import NotificationWebsocketMixin


class ExampleNotificationWebsocket(NotificationWebsocketMixin):
    @classmethod
    def send_example_notification_to_tip_owner(cls, example, updated):
        actor = example.added_by
        if updated:
            actor = example.updated_by

        if example.tip and actor.id != example.tip.added_by_id:
            Notification.objects.create(
                level="success",
                verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE,
                description=format_lazy(
                    _("Example {headline} connected to a tip {title}"),
                    headline=example.headline,
                    title=example.tip.title,
                ),
                actor=actor,
                action_object=example,
                target=example.tip,
                recipient=example.tip.added_by,
            )

            cls.send_new_notification_to_websocket(example.tip.added_by_id)
