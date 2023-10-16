from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

import constants


class TipRatingNotification:
    def generate_tip_rating_creation_notification(self):
        from main.models import User

        added_by = self.added_by

        manager_users = User.objects.managers()

        notifications = [
            {
                "sender": added_by,
                "recipient": added_by,
                "description": format_lazy(
                    _("You have rated tip {title} {stars} stars"),
                    title=self.tip.title,
                    stars=self.stars,
                ),
                "verb": constants.Activity.RATE_TIP,
                "action_object": self.tip,
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
                            "Teacher {user_fullname} has rated tip "
                            "{title} {stars} stars"
                        ),
                        user_fullname=added_by.full_name,
                        title=self.tip.title,
                        stars=self.stars,
                    ),
                    "verb": constants.Activity.RATE_TIP,
                    "action_object": self.tip,
                    "target": self,
                    "level": "info",
                    "timestamp": self.created_at,
                },
            )

        return notifications

    def generate_read_tip_rating_notification(self):
        notifications = [
            {
                "sender": self.added_by,
                "recipient": self.added_by,
                "description": format_lazy(
                    _("{user_fullname} read the tip {title}"),
                    user_fullname=self.added_by.full_name,
                    title=self.tip.title,
                ),
                "verb": constants.Activity.READ_TIP,
                "action_object": self.tip,
                "target": self,
                "level": "success",
                "timestamp": self.updated_at,
            }
        ]

        return notifications

    def generate_try_tip_rating_notification(self):
        notifications = [
            {
                "sender": self.added_by,
                "recipient": self.added_by,
                "description": format_lazy(
                    _("{user_fullname} tried the tip {title}"),
                    user_fullname=self.added_by.full_name,
                    title=self.tip.title,
                ),
                "verb": constants.Activity.TRY_TIP,
                "action_object": self.tip,
                "target": self,
                "level": "success",
                "timestamp": self.updated_at,
            }
        ]

        return notifications

    def generate_comment_tip_rating_notification(self):
        notifications = [
            {
                "sender": self.added_by,
                "recipient": self.added_by,
                "description": format_lazy(
                    _("{user_fullname} commented the tip {title}"),
                    user_fullname=self.added_by.full_name,
                    title=self.tip.title,
                ),
                "verb": constants.Activity.COMMENT_TIP,
                "action_object": self.tip,
                "target": self,
                "level": "success",
                "timestamp": self.updated_at,
            }
        ]

        return notifications
