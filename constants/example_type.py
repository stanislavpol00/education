from django.utils.translation import gettext_lazy as _


class ExampleType:
    ANECDOTAL_TYPE = "ANECDOTAL_EXAMPLE"
    HIGH_FREQUENCY_TYPE = "HIGH_FREQUENCY_EXAMPLE"

    CHOICES = [
        (ANECDOTAL_TYPE, _("Example (Anecdotal)")),
        (HIGH_FREQUENCY_TYPE, _("High Frequency Example (testing by CFC)")),
    ]
