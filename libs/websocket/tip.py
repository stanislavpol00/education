from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from notifications.models import Notification

import constants

from .notification_websocket import NotificationWebsocketMixin


class TipNotificationWebsocket(NotificationWebsocketMixin):
    @classmethod
    def send_editing_notification_to_tip_owner(cls, tip):
        if tip.updated_by_id == tip.added_by_id:
            return

        Notification.objects.create(
            verb=constants.Activity.SET_TIP_EDIT_MARK,
            description=format_lazy(
                _("Tip {title} was marked for editing"), title=tip.title
            ),
            actor=tip.updated_by,
            action_object=tip,
            recipient=tip.added_by,
        )

        cls.send_new_notification_to_websocket(tip.added_by_id)

    @classmethod
    def send_linked_tip_notification_to_linked_tip_owner(cls, tip):
        for linked_tip in tip.linked_tips.all():
            Notification.objects.create(
                verb=constants.Activity.ATTACH_RELATED_TIPS_WITH_TIP,
                description=format_lazy(
                    _("Tip {title1} was marked as related to tip {title2}"),
                    title1=linked_tip.title,
                    title2=tip.title,
                ),
                actor=tip.added_by,
                action_object=linked_tip,
                recipient=linked_tip.added_by,
            )

            cls.send_new_notification_to_websocket(linked_tip.added_by_id)
