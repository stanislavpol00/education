import reversion
from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

import constants
from libs.base_model import BaseModel

from ..querysets import TipQuerySet
from .notification import TipNotification


@reversion.register()
class Tip(BaseModel, TipNotification):
    objects = TipQuerySet.as_manager()

    tags = TaggableManager()

    id = models.AutoField(primary_key=True)
    state = models.CharField(
        verbose_name=_("State of Play"),
        max_length=20,
        choices=constants.States.CHOICES,
        default=constants.States.PAUSING,
    )
    substate = models.CharField(
        verbose_name=_("Sub-State of Play"),
        max_length=20,
        choices=constants.SubStates.CHOICES,
        default=constants.SubStates.ACCOMMODATE,
    )
    levels = models.CharField(
        verbose_name=_("The Five Levels"),
        max_length=20,
        choices=constants.Levels.CHOICES,
        default=constants.Levels.LEVEL_1,
    )
    title = models.CharField(
        max_length=255, verbose_name=_("Title of the tip")
    )
    description = models.TextField(
        verbose_name=_("Description of the tip"), null=True, blank=True
    )
    when = models.TextField(verbose_name=_("When"), null=True, blank=True)
    group_context = models.TextField(
        verbose_name=_("Group context"), null=True, blank=True
    )
    persuasive = models.TextField(
        verbose_name=_("Persuasive of the tip"), null=True, blank=True
    )
    howto = models.TextField(verbose_name=_("How to"), null=True, blank=True)
    helpful = models.TextField(
        verbose_name=_("Helpful"), null=True, blank=True
    )
    sub_goal = models.TextField(
        verbose_name=_("Sub Goal"), null=True, blank=True
    )
    related_tips = models.TextField(
        verbose_name=_("Related Tips"), null=True, blank=True
    )
    overarching_goal = models.TextField(
        verbose_name=_("Overarching Goal"), null=True, blank=True
    )

    child_context = models.JSONField(null=True)
    child_context_flattened = models.TextField(
        null=True,
        blank=True,
    )

    environment_context = models.JSONField(null=True)
    environment_context_flattened = models.TextField(
        null=True,
        blank=True,
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User that updated the tip"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="updated_tips",
    )
    note = models.TextField(verbose_name=_("Change note"), default="")
    linked_tips = models.ManyToManyField("self", blank=True)
    marked_for_editing = models.BooleanField(
        verbose_name=_("Marked for editing"), default=False
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User that added the tip"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="added_tips",
    )

    helpful_count = models.IntegerField(default=0)

    tip_summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return "Tip: %s" % self.title

    class Meta:
        unique_together = ["state", "substate", "levels", "title"]

    @property
    def updated_by_username(self):
        return self.updated_by.username

    @cached_property
    def average_ratings(self):
        average_ratings = self.tiprating_set.aggregate(
            clarity_average_rating=Avg("clarity"),
            relevance_average_rating=Avg("relevance"),
            uniqueness_average_rating=Avg("uniqueness"),
        )
        average_ratings["average_rating"] = None
        if average_ratings["clarity_average_rating"] is not None:
            average_ratings["average_rating"] = (
                average_ratings["clarity_average_rating"]
                + average_ratings["relevance_average_rating"]
                + average_ratings["uniqueness_average_rating"]
            ) / 3.0
            average_ratings["average_rating"] = round(
                average_ratings["average_rating"], 2
            )

        return average_ratings

    @cached_property
    def clarity_average_rating(self):
        return self.average_ratings["clarity_average_rating"]

    @cached_property
    def relevance_average_rating(self):
        return self.average_ratings["relevance_average_rating"]

    @cached_property
    def uniqueness_average_rating(self):
        return self.average_ratings["uniqueness_average_rating"]

    @cached_property
    def average_rating(self):
        return self.average_ratings["average_rating"]

    def _extrace_context_values(self, context_data):
        values = []
        for value in context_data:
            if isinstance(value, dict) and "value" in value:
                value = str(value["value"])
            if value and not isinstance(value, str):
                value = str(value)

            value = value.strip() if value else None
            if value:
                values.append(value)
        return values[:3]

    def auto_update_context_flattened_fields(self):
        if not self.child_context_flattened and self.child_context:
            try:
                context_data = sorted(
                    self.child_context.values(),
                    key=lambda context: context["order"],
                )
            except Exception:
                context_data = self.child_context.values()

            values = self._extrace_context_values(context_data)
            if values:
                self.child_context_flattened = "\n".join(values)

        if not self.environment_context_flattened and self.environment_context:
            try:
                context_data = sorted(
                    self.environment_context.values(),
                    key=lambda context: context["order"],
                )
            except Exception:
                context_data = self.environment_context.values()

            values = self._extrace_context_values(context_data)
            if values:
                self.environment_context_flattened = "\n".join(values)

    def save(self, *args, **kwargs):
        self.auto_update_context_flattened_fields()

        instance = super().save(*args, **kwargs)

        return instance
