from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

import constants


class StudentExampleNotification:
    def generate_student_example_creation_notification(self):
        student_added_by = self.student.added_by
        if not student_added_by or not self.added_by:
            return []

        return [
            {
                "sender": self.added_by,
                "recipient": student_added_by,
                "description": format_lazy(
                    _(
                        "A example {headline} is assigned to "
                        "your student {user_fullname}"
                    ),
                    headline=self.example.headline,
                    user_fullname=self.student.full_name,
                ),
                "verb": constants.Activity.ASSIGN_EXAMPLE_TO_STUDENT,
                "action_object": self.example,
                "target": self.student,
                "level": "info",
                "timestamp": self.created_at,
            }
        ]
