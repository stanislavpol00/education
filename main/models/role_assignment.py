from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models

from libs.base_model import BaseModel

from ..querysets import RoleAssignmentQuerySet


class RoleAssignment(BaseModel):
    objects = RoleAssignmentQuerySet.as_manager()

    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
    )

    organization = models.ForeignKey(
        "Organization",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ("user", "organization")
