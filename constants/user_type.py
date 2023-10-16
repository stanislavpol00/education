from django.utils.translation import gettext_lazy as _


class UserType:
    ADMIN = "ADMIN"
    EDUCATOR_SHADOW = "EDUCATOR_SHADOW"
    EDUCATOR_CONTENT_EXPERT = "EDUCATOR_CONTENT_EXPERT"
    GUEST = "GUEST"
    PARENT = "PARENT"

    CHOICES = (
        (ADMIN, _("Administrator")),
        (EDUCATOR_SHADOW, _("Educator Shadow")),
        (EDUCATOR_CONTENT_EXPERT, _("Educator Content Expert")),
        (GUEST, _("Guest")),
        (PARENT, _("Parent")),
    )

    ALL = (
        ADMIN,
        EDUCATOR_SHADOW,
        EDUCATOR_CONTENT_EXPERT,
        GUEST,
        PARENT,
    )
