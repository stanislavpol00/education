from django.utils.translation import gettext_lazy as _


class ChildContext:
    CURRENT_MOTIVATOR = "CURRENT_MOTIVATOR"
    ANTICIPATED_MOTIVATOR = "ANTICIPATED_MOTIVATOR"
    CURRENT_BEHAVIOR = "CURRENT_BEHAVIOR"
    ANTICIPATED_BEHAVIOR = "ANTICIPATED_BEHAVIOR"

    CHOICES = [
        (CURRENT_MOTIVATOR, _("Current Motivator")),
        (ANTICIPATED_MOTIVATOR, _("Anticipated Motivator")),
        (CURRENT_BEHAVIOR, _("Current Behavior")),
        (ANTICIPATED_BEHAVIOR, _("Anticipated Behavior")),
    ]

    VALUES = [
        CURRENT_MOTIVATOR,
        ANTICIPATED_MOTIVATOR,
        CURRENT_BEHAVIOR,
        ANTICIPATED_BEHAVIOR,
    ]
