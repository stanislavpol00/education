from django.utils.translation import gettext_lazy as _


class Relevance:
    RELEVANT_FOR_THIS_WEEK = "RELEVANT_FOR_THIS_WEEK"
    NOT_RELEVANT_RIGHT_NOW = "NOT_RELEVANT_RIGHT_NOW"
    CHOICES = (
        ("RELEVANT_FOR_THIS_WEEK", _("Relevant for this week")),
        ("NOT_RELEVANT_RIGHT_NOW", _("Not relevant right now")),
    )

    MAPS = {
        RELEVANT_FOR_THIS_WEEK: 5,
        NOT_RELEVANT_RIGHT_NOW: 2,
    }
