from django.utils.translation import gettext_lazy as _


class SubStates:
    ACCOMMODATE = "ACCOMMODATE"
    REMEDIATE = "REMEDIATE"
    CHOICES = [
        (ACCOMMODATE, _("Accommodate")),
        (REMEDIATE, _("Remediate")),
    ]

    ACCOMODATE = "ACCOMODATE"
    MAPS = {
        ACCOMODATE: ACCOMMODATE,
        REMEDIATE: REMEDIATE,
        ACCOMMODATE: ACCOMMODATE,
    }
