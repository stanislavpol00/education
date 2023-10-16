from django.utils.translation import gettext_lazy as _

from .group import Group


class Role:
    ADMIN_USER = 1
    EDUCATOR_SHADOW = 2
    EDUCATOR_CONTENT_EXPERT = 3
    GUEST = 4
    EXPERIMENTAL_TEACHER = 5
    MANAGER = 6

    CHOICES = (
        (ADMIN_USER, _("Administrator User")),
        (EDUCATOR_SHADOW, _("Educator Shadow")),
        (EDUCATOR_CONTENT_EXPERT, _("Educator Content Expert")),
        (EXPERIMENTAL_TEACHER, _("Experimental Teacher")),
        (GUEST, _("Guest")),
        (MANAGER, _("Manager")),
    )

    MANAGERS = [MANAGER, ADMIN_USER]

    EDUCATORS = [EDUCATOR_SHADOW, EDUCATOR_CONTENT_EXPERT]

    ROLE_TO_GROUP_NAME = {
        ADMIN_USER: Group.ORGANIZATION_ADMIN,
        MANAGER: Group.ORGANIZATION_ADMIN,
        EXPERIMENTAL_TEACHER: Group.ORGANIZATION_DLP,
        GUEST: Group.ORGANIZATION_GUEST,
    }

    @staticmethod
    def role_to_group_name(role):
        return Role.ROLE_TO_GROUP_NAME.get(role, Group.ORGANIZATION_STAFF)
