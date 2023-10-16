from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from libs.base_model import BaseModel

from ..querysets import StudentTipQuerySet
from .notification import StudentTipNotification


class StudentTip(BaseModel, StudentTipNotification):
    objects = StudentTipQuerySet.as_manager()

    id = models.AutoField(primary_key=True)

    tip = models.ForeignKey("Tip", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_added_by",
    )

    is_graduated = models.BooleanField(
        verbose_name=_("Is Graduated"), default=False
    )

    last_used_at = models.DateTimeField(null=True)

    last_suggested_at = models.DateTimeField(null=True)

    is_queued = models.BooleanField(default=False)

    class Meta:
        unique_together = [("tip", "student")]
