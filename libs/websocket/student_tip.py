from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from notifications.models import Notification

import constants
from main.models import User

from .notification_websocket import NotificationWebsocketMixin


class StudentTipNotificationWebsocket(NotificationWebsocketMixin):
    @classmethod
    def send_new_student_tip_notification(cls, student_tip):
        cls.send_student_tip_notification_to_mapped_users(student_tip)

    @classmethod
    def send_student_tip_notification_to_mapped_users(cls, student_tip):
        mapped_user_ids = student_tip.student.experimental_student.exclude(
            user_id=student_tip.added_by_id
        ).values_list("user_id")

        mapped_users = User.objects.filter(
            pk__in=mapped_user_ids,
        )

        for mapped_user in mapped_users:
            Notification.objects.create(
                level="success",
                verb=constants.Activity.SUGGEST_TIP,
                description=format_lazy(
                    _(
                        "{user_fullname} suggest a tip for "
                        "the student {student_fullname}"
                    ),
                    user_fullname=student_tip.added_by.full_name,
                    student_fullname=student_tip.student.full_name,
                ),
                actor=student_tip.added_by,
                action_object=student_tip,
                recipient=mapped_user,
                timestamp=student_tip.created_at,
            )

            cls.send_new_notification_to_websocket(mapped_user.id)
