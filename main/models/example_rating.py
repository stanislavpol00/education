from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from libs.base_model import BaseModel

from ..querysets import ExampleRatingQuerySet
from .notification import ExampleRatingNotification


class ExampleRating(BaseModel, ExampleRatingNotification):
    objects = ExampleRatingQuerySet.as_manager()

    id = models.AutoField(primary_key=True)
    example = models.ForeignKey("Example", on_delete=models.CASCADE)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User that rated the example"),
        null=True,
        on_delete=models.SET_NULL,
    )

    clarity = models.FloatField(
        default=1, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    recommended = models.FloatField(
        default=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name=_("How likely to recommend to a colleague"),
    )
    comment = models.TextField(default="")

    def __str__(self):
        return _("Example Rating: {headline}").format(
            headline=self.example.headline
        )

    @property
    def stars(self):
        total = self.clarity + self.recommended
        stars = round(total / 2.0, 2)
        return stars
