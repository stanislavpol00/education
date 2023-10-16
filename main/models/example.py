import reversion
from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

import constants
from libs.base_model import BaseModel

from ..querysets import ExampleQuerySet
from .notification import ExampleNotification


@reversion.register()
class Example(BaseModel, ExampleNotification):
    objects = ExampleQuerySet.as_manager()

    tags = TaggableManager()

    id = models.AutoField(primary_key=True)
    tip = models.ForeignKey(
        "Tip",
        verbose_name=_("Tip of this example"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        verbose_name=_("Description of the example")
    )
    example_type = models.CharField(
        verbose_name=_("Example type"),
        max_length=60,
        choices=constants.ExampleType.CHOICES,
        default=constants.ExampleType.ANECDOTAL_TYPE,
    )
    context_notes = models.TextField(
        verbose_name=_("Context notes"), default="", null=True, blank=True
    )
    sounds_like = models.TextField(
        verbose_name=_("Sounds like"), default="", null=True, blank=True
    )
    looks_like = models.TextField(
        verbose_name=_("Looks like"), default="", null=True, blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_examples",
        verbose_name=_("User that updated example"),
        on_delete=models.SET_NULL,
        null=True,
    )
    episode = models.ForeignKey(
        "Episode", on_delete=models.CASCADE, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    goal = models.TextField(
        verbose_name=_("Goal that motivated the example"), default=""
    )
    is_workflow_completed = models.BooleanField(
        verbose_name=_("Workflow completed"), default=True
    )
    is_bookmarked = models.BooleanField(default=False)

    headline = models.CharField(max_length=255, verbose_name=_("Headline"))
    heading = models.CharField(max_length=255, verbose_name=_("Heading"))

    situation = models.TextField(verbose_name=_("Situation"), null=True)
    shadows_response = models.TextField(
        verbose_name=_("Shadows response"), null=True
    )
    outcome = models.TextField(verbose_name=_("Outcome"), null=True)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_examples",
        verbose_name=_("User that added example"),
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        unique_together = [("tip", "description")]

    @property
    def updated_by_username(self):
        return self.updated_by.username

    @cached_property
    def average_ratings(self):
        average_ratings = self.examplerating_set.aggregate(
            clarity_average_rating=Avg("clarity"),
            recommended_average_rating=Avg("recommended"),
        )
        average_ratings["average_rating"] = None
        if average_ratings["clarity_average_rating"] is not None:
            average_ratings["average_rating"] = (
                average_ratings["clarity_average_rating"]
                + average_ratings["recommended_average_rating"]
            ) / 2.0
            average_ratings["average_rating"] = round(
                average_ratings["average_rating"], 2
            )

        return average_ratings

    @cached_property
    def clarity_average_rating(self):
        return self.average_ratings["clarity_average_rating"]

    @cached_property
    def recommended_average_rating(self):
        return self.average_ratings["recommended_average_rating"]

    @cached_property
    def average_rating(self):
        return self.average_ratings["average_rating"]

    @cached_property
    def episode_student_id(self):
        if self.episode:
            return self.episode.student_id

    @cached_property
    def student_ids(self):
        return list(
            self.studentexample_set.values_list("student_id", flat=True)
        )
