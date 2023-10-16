from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

import constants
from libs.base_model import BaseModel

from ..managers import TaskManager


class Task(BaseModel):
    objects = TaskManager()

    id = models.AutoField(primary_key=True)
    task_type = models.CharField(
        verbose_name=_("Task type"),
        max_length=15,
        null=True,
        choices=constants.TaskType.CHOICES,
    )
    info = models.TextField(verbose_name=_("Information"))
    reporter_note = models.TextField(
        verbose_name=_("Reporter note"), null=True
    )
    assignee_note = models.TextField(
        verbose_name=_("Assignee note"), null=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )
    tip = models.ForeignKey(
        "Tip", verbose_name=_("Tip to apply"), on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        "Student", verbose_name=_("Student"), on_delete=models.CASCADE
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="added_task_set",
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )

    class Meta:
        unique_together = [("user", "tip", "student")]
