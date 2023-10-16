from django.utils.translation import gettext_lazy as _


class StudentExample:
    REASON_EPISODE = "EPISODE"
    REASON_INCLUDED = "INCLUDED"
    REASON_INAPPROPRIATE = "INAPPROPRIATE"
    REASON_GENERATED = "GENERATED"

    REASON_CHOICES = (
        (REASON_EPISODE, _("Generated the example")),
        (REASON_INCLUDED, _("Included by an educator")),
        (REASON_INAPPROPRIATE, _("It's inappropriate for the child")),
        (REASON_GENERATED, _("This example was generated for the student")),
    )
