from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

import constants


class TipNotification:
    def generate_tip_creation_notification(self):
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
                    _("You have created a new tip {title}"),
                    title=self.title,
                ),
                "verb": constants.Activity.CREATE_TIP,
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
                            "a new tip {title}"
                        ),
                        user_fullname=added_by.full_name,
                        title=self.title,
                    ),
                    "verb": constants.Activity.CREATE_TIP,
                    "action_object": self,
                    "level": "info",
                    "timestamp": self.created_at,
                },
            )

        return notifications

    def generate_tip_updating_notification(self):
        added_by = self.added_by
        updated_by = self.updated_by
        if not added_by or not updated_by:
            return []

        description = format_lazy(
            _("You just have updated tip {title}"), title=self.title
        )
        notifications = [
            {
                "sender": updated_by,
                "recipient": updated_by,
                "description": description,
                "verb": constants.Activity.UPDATE_TIP,
                "action_object": self,
                "level": "success",
                "timestamp": self.updated_at,
            }
        ]

        if added_by.id != updated_by.id:
            description = format_lazy(
                _("Your tip {title} is updated by Teacher {user_fullname}"),
                title=self.title,
                user_fullname=updated_by.full_name,
            )
            notifications.append(
                {
                    "sender": updated_by,
                    "recipient": added_by,
                    "description": description,
                    "verb": constants.Activity.UPDATE_TIP,
                    "action_object": self,
                    "level": "info",
                    "timestamp": self.updated_at,
                }
            )

        return notifications

    def generate_set_tip_edit_mark_notification(self):
        notifications = [
            {
                "sender": self.updated_by,
                "recipient": self.updated_by,
                "description": format_lazy(
                    _("You were marked tip {title} for editing"),
                    title=self.title,
                ),
                "verb": constants.Activity.SET_TIP_EDIT_MARK,
                "action_object": self,
                "level": "success",
                "timestamp": self.updated_at,
            }
        ]

        return notifications

    def generate_attach_tip_notifications(self, attached_tip_ids):
        attached_tips = self.__class__.objects.filter(
            pk__in=attached_tip_ids
        ).values("title")

        notifications = [
            {
                "sender": self.updated_by,
                "recipient": self.updated_by,
                "description": format_lazy(
                    _("You were attached tip {title1} with tip {title2}"),
                    title1=self.title,
                    title2=attached_tip["title"],
                ),
                "verb": constants.Activity.ATTACH_RELATED_TIPS_WITH_TIP,
                "action_object": self,
                "level": "success",
                "timestamp": self.updated_at,
            }
            for attached_tip in attached_tips
        ]

        return notifications

    def generate_detach_tip_notifications(self, detached_tip_ids):
        detached_tips = self.__class__.objects.filter(
            pk__in=detached_tip_ids
        ).values("title")

        notifications = [
            {
                "sender": self.updated_by,
                "recipient": self.updated_by,
                "description": format_lazy(
                    _("You were detached tip {title1} with tip {title2}"),
                    title1=self.title,
                    title2=detached_tip["title"],
                ),
                "verb": constants.Activity.DETACH_RELATED_TIPS_WITH_TIP,
                "action_object": self,
                "level": "success",
                "timestamp": self.updated_at,
            }
            for detached_tip in detached_tips
        ]

        return notifications
