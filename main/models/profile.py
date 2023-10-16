from django.conf import settings
from django.db import models

import constants
from libs.base_model import BaseModel

from ..querysets import ProfileQuerySet


class Profile(BaseModel):
    objects = ProfileQuerySet.as_manager()

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    usertype = models.CharField(
        max_length=25,
        choices=constants.UserType.CHOICES,
        default=constants.UserType.EDUCATOR_SHADOW,
    )
    photo_width = models.IntegerField(default=0)
    photo_height = models.IntegerField(default=0)
    photo = models.ImageField(
        default=None,
        max_length=100,
        null=True,
        blank=True,
        width_field="photo_width",
        height_field="photo_height",
    )
