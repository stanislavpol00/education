from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from libs.base_model import BaseModel

from ..querysets import TipRatingQuerySet
from .notification import TipRatingNotification


class TipRating(BaseModel, TipRatingNotification):
    objects = TipRatingQuerySet.as_manager()

    id = models.AutoField(primary_key=True)
    tip = models.ForeignKey("Tip", on_delete=models.CASCADE)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User that rated the tip"),
        on_delete=models.CASCADE,
    )

    student = models.ForeignKey(
        "Student",
        null=True,
        on_delete=models.SET_NULL,
    )

    clarity = models.FloatField(
        default=0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    relevance = models.FloatField(
        default=0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    uniqueness = models.FloatField(
        default=0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    comment = models.TextField(default="")
    commented_at = models.DateTimeField(default=None, blank=True, null=True)

    read_count = models.IntegerField(default=0)
    try_count = models.IntegerField(default=0)
    try_comment = models.CharField(
        verbose_name=_("Try Comment"),
        max_length=200,
        default=None,
        blank=True,
        null=True,
    )
    tried_at = models.DateTimeField(default=None, blank=True, null=True)

    retry_later = models.BooleanField(default=True)

    helpful_count = models.IntegerField(default=0)

    def __str__(self):
        return _("Tip Rating: {title}").format(title=self.tip.title)

    @property
    def stars(self):
        total = self.clarity + self.relevance + self.uniqueness
        stars = round(total / 3.0, 2)
        return stars

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("added_by", "tip", "student"),
                name="unique_3_fields_together",
            ),
            UniqueConstraint(
                fields=("added_by", "tip", "student"),
                condition=Q(student__isnull=True),
                name="unique_3_fields_together_with_conditions",
            ),
        ]
