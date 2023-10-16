from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

import constants


class StudentTipNotification:
    def generate_student_tip_creation_notification(self):
        student_added_by = self.student.added_by
        if not student_added_by or not self.added_by:
            return []

        return [
            {
                "sender": self.added_by,
                "recipient": student_added_by,
                "description": format_lazy(
                    _(
                        "A tip {title} is assigned to "
                        "your student {user_fullname}"
                    ),
                    title=self.tip.title,
                    user_fullname=self.student.full_name,
                ),
                "verb": constants.Activity.ASSIGN_TIP_TO_STUDENT,
                "action_object": self.tip,
                "target": self.student,
                "level": "info",
                "timestamp": self.created_at,
            },
            {
                "sender": self.added_by,
                "recipient": self.added_by,
                "description": format_lazy(
                    _(
                        "{teacher_fullname} assigned the tip {title} for "
                        "the student {student_fullname}"
                    ),
                    teacher_fullname=self.added_by.full_name,
                    title=self.tip.title,
                    student_fullname=self.student.full_name,
                ),
                "verb": constants.Activity.SUGGEST_TIP,
                "action_object": self,
                "target": self.student,
                "level": "success",
                "timestamp": self.created_at,
            },
        ]
