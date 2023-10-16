from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from notifications.models import Notification

import constants
from main.models import User

from .notification_websocket import NotificationWebsocketMixin


class EpisodeNotificationWebsocket(NotificationWebsocketMixin):
    @classmethod
    def send_new_episode_notification(cls, episode):
        cls.send_episode_notification_to_mapped_users(episode)

    @classmethod
    def send_episode_notification_to_mapped_users(cls, episode):
        mapped_user_ids = episode.student.experimental_student.exclude(
            user_id=episode.user_id
        ).values_list("user_id")

        mapped_users = User.objects.filter(pk__in=mapped_user_ids)

        for mapped_user in mapped_users:
            Notification.objects.create(
                level="success",
                verb=constants.Activity.CREATE_EPISODE,
                description=format_lazy(
                    _(
                        "{user_fullname} created a episode for "
                        "the student {student_fullname}"
                    ),
                    user_fullname=episode.user.full_name,
                    student_fullname=episode.student.full_name,
                ),
                actor=episode.user,
                action_object=episode,
                recipient=mapped_user,
                timestamp=episode.created_at,
            )

            cls.send_new_notification_to_websocket(mapped_user.id)
