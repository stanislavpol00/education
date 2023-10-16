from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from libs.base_model import BaseModel

from ..querysets import EpisodeQuerySet


class Episode(BaseModel):
    objects = EpisodeQuerySet.as_manager()

    tags = TaggableManager()

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        "Student",
        verbose_name=_("Student for the episode"),
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Educator that created the episode"),
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    description_html = models.TextField(
        verbose_name=_("HTML Description of the episode"),
        null=True,
        blank=True,
    )
    description_ids = models.TextField(
        verbose_name=_("HTML Description IDS of the episode"),
        null=True,
        blank=True,
    )
    transcript_html = models.TextField(
        verbose_name=_("HTML Transcript of the episode"), null=True, blank=True
    )
    transcript = models.TextField(
        verbose_name=_("Transcript"), null=True, blank=True
    )
    transcript_ids = models.TextField(
        verbose_name=_("HTML Transcript IDS of the episode"),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    date = models.DateTimeField()
    full = models.BooleanField(
        verbose_name=_("Fully entered in grid"), default=False
    )
    landmark = models.BooleanField(
        verbose_name=_("landmark episode"), default=False
    )

    # later on heads_up should be remove, heads_up_json name should be changed
    heads_up = models.TextField(
        verbose_name=_("Heads Up"), null=True, blank=True
    )
    heads_up_json = models.JSONField(verbose_name=_("Heads Up"), null=True)

    practitioner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Educator that contributed the episode"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="contributed_episodes",
    )

    @cached_property
    def writers(self):
        examples = self.example_set.all()

        added_bys = set([example.added_by for example in examples])

        return list(added_bys)

    @cached_property
    def contributors(self):
        added_bys = self.writers

        return added_bys
