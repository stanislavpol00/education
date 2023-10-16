from django.utils.translation import gettext_lazy as _


class StudentTip:
    REASON_SUGGESTED = "SUGGESTED"
    REASON_STARRED = "STARRED"
    REASON_USED = "USED"
    REASON_CHOICES = (
        (REASON_SUGGESTED, _("The tip has been suggested for this child")),
        (
            REASON_STARRED,
            _(
                "The child has shown a lot of improvement, and the tip is no longer needed"
            ),
        ),
        (REASON_USED, _("The child has used this strategy and has examples")),
    )

    RATE_CLEAR = "CLEAR"
    RATE_SORT_OF_UNDERSTANDABLE = "SORT_OF_UNDERSTANDABLE"
    RATE_CONFUSING = "CONFUSING"
    RATE_CHOICES = (
        (RATE_CLEAR, _("Clear")),
        (RATE_SORT_OF_UNDERSTANDABLE, _("Sort of understandable")),
        (RATE_CONFUSING, _("Confusing")),
    )

    RELEVANCE_RELEVANT_FOR_THIS_WEEK = "RELEVANT_FOR_THIS_WEEK"
    RELEVANCE_NOT_RELEVANT_RIGHT_NOW = "NOT_RELEVANT_RIGHT_NOW"
    RELEVANCE_CHOICES = (
        (RELEVANCE_RELEVANT_FOR_THIS_WEEK, _("Relevant for this week")),
        (RELEVANCE_NOT_RELEVANT_RIGHT_NOW, _("Not relevant right now")),
    )
