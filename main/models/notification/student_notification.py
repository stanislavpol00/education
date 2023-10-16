from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

import constants


class StudentNotification:
    def generate_student_creation_notification(self):
        from main.models import User

        added_by = self.added_by
        if not added_by:
            return []

        manager_users = User.objects.managers()

        notifications = [
            {
                "sender": added_by,
                "recipient": added_by,
                "description": format_lazy(
                    _("You have added a new student {user_fullname}"),
                    user_fullname=self.full_name,
                ),
                "verb": constants.Activity.CREATE_STUDENT,
                "action_object": self,
                "level": "success",
                "timestamp": self.created_at,
            }
        ]

        if not added_by.is_manager:
            notifications.append(
                {
                    "sender": added_by,
                    "recipient": manager_users,
                    "description": format_lazy(
                        _(
                            "A new student {student_fullname} is created by "
                            "teacher {teacher_fullname}"
                        ),
                        student_fullname=self.full_name,
                        teacher_fullname=added_by.full_name,
                    ),
                    "verb": constants.Activity.CREATE_STUDENT,
                    "action_object": self,
                    "level": "info",
                    "timestamp": self.created_at,
                }
            )

        return notifications
