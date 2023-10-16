from django.utils.translation import gettext_lazy as _


class TaskType:
    EXAMPLE = "EXAMPLE_TASK"
    MISC = "MISC_TASK"

    CHOICES = (
        (EXAMPLE, _("Task with an example")),
        (MISC, _("Task with short notes")),
    )
