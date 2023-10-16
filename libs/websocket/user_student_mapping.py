from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from notifications.models import Notification

import constants

from .notification_websocket import NotificationWebsocketMixin


class UserStudentMappingNotificationWebsocket(NotificationWebsocketMixin):
    @classmethod
    def send_assign_student_notification_to_mapped_user(
        cls, user_student_mapping
    ):
        if user_student_mapping.has_assigned_student_yourself:
            return

        Notification.objects.create(
            verb=constants.Activity.ASSIGN_STUDENT,
            description=format_lazy(
                _(
                    "{user_fullname} assigned "
                    "student {student_fullname} for you"
                ),
                user_fullname=user_student_mapping.added_by.full_name,
                student_fullname=user_student_mapping.student.full_name,
            ),
            actor=user_student_mapping.added_by,
            action_object=user_student_mapping,
            recipient=user_student_mapping.user,
            timestamp=user_student_mapping.date_joined,
        )

        cls.send_new_notification_to_websocket(user_student_mapping.user_id)
