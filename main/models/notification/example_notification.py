from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

import constants


class ExampleNotification:
    def generate_example_creation_notification(self):
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
                    _("You have created a new example {headline}"),
                    headline=self.headline,
                ),
                "verb": constants.Activity.CREATE_EXAMPLE,
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
                            "Teacher {user_fullname} has created "
                            "a new example {headline}"
                        ),
                        user_fullname=added_by.full_name,
                        headline=self.headline,
                    ),
                    "verb": constants.Activity.CREATE_EXAMPLE,
                    "action_object": self,
                    "level": "info",
                    "timestamp": self.created_at,
                }
            )

        return notifications

    def generate_example_updating_notification(self):
        added_by = self.added_by
        updated_by = self.updated_by
        if not added_by or not updated_by:
            return []

        description = format_lazy(
            _("You just have updated example {headline}"),
            headline=self.headline,
        )
        notifications = [
            {
                "sender": updated_by,
                "recipient": updated_by,
                "description": description,
                "verb": constants.Activity.UPDATE_EXAMPLE,
                "action_object": self,
                "level": "success",
                "timestamp": self.updated_at,
            }
        ]

        if added_by.id != updated_by.id:
            description = format_lazy(
                _(
                    "Your example {headline} is updated by "
                    "Teacher {user_fullname}"
                ),
                headline=self.headline,
                user_fullname=updated_by.full_name,
            )
            notifications.append(
                {
                    "sender": updated_by,
                    "recipient": added_by,
                    "description": description,
                    "verb": constants.Activity.UPDATE_EXAMPLE,
                    "action_object": self,
                    "level": "info",
                    "timestamp": self.updated_at,
                }
            )

        return notifications

    def generate_attach_tip_notifications(self, attached_tip):
        actor = self.added_by
        timestamp = self.created_at

        if self.updated_by:
            actor = self.updated_by
            timestamp = self.updated_at

        notifications = [
            {
                "sender": actor,
                "recipient": actor,
                "description": format_lazy(
                    _(
                        "You were connected example {headline} "
                        "with tip {title}"
                    ),
                    headline=self.headline,
                    title=attached_tip.title,
                ),
                "verb": constants.Activity.ATTACH_TIP_WITH_EXAMPLE,
                "action_object": self,
                "level": "success",
                "timestamp": timestamp,
            }
        ]

        return notifications

    def generate_detach_tip_notifications(self, detached_tip):
        notifications = [
            {
                "sender": self.updated_by,
                "recipient": self.updated_by,
                "description": format_lazy(
                    _("You were detach tip {title} from" "example {headline}"),
                    title=detached_tip.title,
                    headline=self.headline,
                ),
                "verb": constants.Activity.DETACH_TIP_FROM_EXAMPLE,
                "action_object": self,
                "level": "success",
                "timestamp": self.updated_at,
            }
        ]

        return notifications
