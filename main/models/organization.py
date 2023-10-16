from django.db import models
from django.utils.translation import gettext_lazy as _

from libs.base_model import BaseModel

from ..querysets import OrganizationQuerySet


class Organization(BaseModel):
    objects = OrganizationQuerySet.as_manager()

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=30,
        verbose_name=_("Organization Name"),
        unique=True,
    )

    def __str__(self):
        return self.name
