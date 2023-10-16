from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

import constants
from libs.base_model import BaseModel

from ..querysets import ActivityQuerySet


class Activity(BaseModel):
    objects = ActivityQuerySet.as_manager()

    id = models.AutoField(primary_key=True)
    type = models.CharField(
        max_length=30,
        verbose_name=_("Type"),
        choices=constants.Activity.CHOICES,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User that created the activity"),
        on_delete=models.CASCADE,
    )

    meta = models.JSONField(verbose_name=_("Meta"), null=True)

    def can_modify(self, user):
        return user.is_manager or self.user_id == user.id
