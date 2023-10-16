from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

import constants


class ExampleRatingNotification:
    def generate_example_rating_creation_notification(self):
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
                    _("You have rated example {headline} {stars} stars"),
                    headline=self.example.headline,
                    stars=self.stars,
                ),
                "verb": constants.Activity.RATE_EXAMPLE,
                "action_object": self.example,
                "target": self,
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
                            "Teacher {user_fullname} has rated example "
                            "{headline} {stars} stars"
                        ),
                        user_fullname=added_by.full_name,
                        headline=self.example.headline,
                        stars=self.stars,
                    ),
                    "verb": constants.Activity.RATE_EXAMPLE,
                    "action_object": self.example,
                    "target": self,
                    "level": "info",
                    "timestamp": self.created_at,
                }
            )

        return notifications
