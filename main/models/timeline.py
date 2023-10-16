from django.db import models
from django.utils.translation import gettext_lazy as _

from ..managers import TimelineManager


class Timeline(models.Model):
    objects = TimelineManager()

    id = models.AutoField(primary_key=True)
    name = models.TextField(verbose_name=_("Name"))
    is_default = models.BooleanField(default=False)
    days = models.IntegerField(default=0)
