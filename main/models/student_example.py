from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

import constants
from libs.base_model import BaseModel

from ..querysets import StudentExampleQuerySet
from .notification import StudentExampleNotification


class StudentExample(BaseModel, StudentExampleNotification):
    objects = StudentExampleQuerySet.as_manager()

    id = models.AutoField(primary_key=True)
    reason = models.CharField(
        verbose_name=_("State of Play"),
        max_length=15,
        choices=constants.StudentExample.REASON_CHOICES,
    )
    example = models.ForeignKey("Example", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = [("example", "student")]
