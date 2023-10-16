from celery import shared_task
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from notifications.models import Notification

import constants
from main.models import User
from libs.websocket.notification_websocket import NotificationWebsocketMixin


@shared_task
def rating_reminder():
    users = User.objects.annotate_number_tip_rating_reminder()

    for user in users:
        Notification.objects.create(
            verb=constants.Activity.RATING_REMINDER,
            description=format_lazy(
                _("You have {number} tips awaiting your review."),
                number=user.number_of_tips,
            ),
            actor=user,
            recipient=user,
        )

        NotificationWebsocketMixin.send_new_notification_to_websocket(user.id)
