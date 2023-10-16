from django.utils.translation import gettext_lazy as _


class Levels:
    LEVEL_1 = "1"
    LEVEL_2 = "2"
    LEVEL_3 = "3"
    LEVEL_4 = "4"
    LEVEL_5 = "5"
    CHOICES = [
        (LEVEL_1, _("From avoidance to tolerance")),
        (LEVEL_2, _("From tolerance to proximity")),
        (LEVEL_3, _("From proximity to interaction")),
        (LEVEL_4, _("From interaction to flow")),
        (LEVEL_5, _("From flow to planning")),
    ]

    DESCRIPTIONS = [
        (LEVEL_1, _("Relief, comfort, escape")),
        (LEVEL_2, _("Physical objects, control, repetition")),
        (LEVEL_3, _("Social moments, reactions, flickers of connection")),
        (LEVEL_4, _("Relationships, influence, interactive play")),
        (LEVEL_5, _("Continuity, predictability, self improvement")),
    ]

    MAPS = {
        "1Y": LEVEL_1,
        "2Y": LEVEL_2,
        "3Y": LEVEL_3,
        "4Y": LEVEL_4,
        "5Y": LEVEL_5,
    }
