from django.utils.translation import gettext_lazy as _


class States:
    PAUSING = "PAUSING"
    ENTERING = "ENTERING"
    SUSTAINING = "SUSTAINING"
    TRANSITIONING = "TRANSITIONING"
    CHOICES = [
        (PAUSING, _("Pausing the Activity")),
        (ENTERING, _("Entering the Activity")),
        (SUSTAINING, _("Sustaining the Activity")),
        (TRANSITIONING, _("Transitioning the Activity")),
    ]

    X1 = "1X"
    X2 = "2X"
    X3 = "3X"
    X4 = "4X"
    MAPS = {
        X1: PAUSING,
        X2: ENTERING,
        X3: SUSTAINING,
        X4: TRANSITIONING,
    }
