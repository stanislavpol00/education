from django.utils.translation import gettext_lazy as _


class Clarity:
    CLEAR = "CLEAR"
    SORT_OF_UNDERSTANDABLE = "SORT_OF_UNDERSTANDABLE"
    CONFUSING = "CONFUSING"
    CHOICES = (
        (CLEAR, _("Clear")),
        (SORT_OF_UNDERSTANDABLE, _("Sort of understandable")),
        (CONFUSING, _("Confusing")),
    )

    MAPS = {
        CLEAR: 5,
        SORT_OF_UNDERSTANDABLE: 3,
        CONFUSING: 1,
    }
