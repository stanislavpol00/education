from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from libs.base_model import BaseModel

from ..querysets import StudentQuerySet
from .notification import StudentNotification


class Student(BaseModel, StudentNotification):
    objects = StudentQuerySet.as_manager()

    tags = TaggableManager()

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, verbose_name=_("Given name"))
    last_name = models.CharField(max_length=255, verbose_name=_("Last name"))
    nickname = models.CharField(
        max_length=255, verbose_name=_("Nickname"), default=""
    )
    tips = models.ManyToManyField("Tip", through="StudentTip")
    examples = models.ManyToManyField("Example", through="StudentExample")

    is_active = models.BooleanField(default=True)
    image = models.ImageField(null=True, blank=True)
    visible_for_guest = models.BooleanField(
        verbose_name=_("Visible for guest"), default=False
    )

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_added_by",
    )

    def __str__(self):
        return _("Student: {nickname}").format(nickname=self.nickname)

    @property
    def heads_up(self):
        heads_up_list = []
        for episode in self.episode_set.order_by("-id"):
            if not episode.heads_up_json:
                continue
            heads_up = episode.heads_up_json
            heads_up["date"] = episode.date
            heads_up["episode"] = episode.id
            heads_up_list.append(heads_up)

        return heads_up_list

    @property
    def last_month_heads_up(self):
        last_month = timezone.localtime() - timezone.timedelta(days=30)
        last_month_episodes = self.episode_set.filter(
            date__gte=last_month
        ).order_by("-id")

        heads_up_list = []
        for episode in last_month_episodes:
            if not episode.heads_up_json:
                continue
            heads_up = episode.heads_up_json
            heads_up["date"] = episode.date
            heads_up["episode"] = episode.id
            heads_up_list.append(heads_up)

        return heads_up_list

    @property
    def last_episode(self):
        return self.episode_set.order_by("-id").first()

    @property
    def monitoring(self):
        if self.last_episode:
            return self.last_episode.heads_up_json.get("monitoring")

        return None

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def full_name(self):
        return self.get_full_name()

    def dequeue_tips(self, number_of_tips):
        queued_tips = self.studenttip_set.filter(is_queued=True).order_by("?")[
            :number_of_tips
        ]
        queued_tips = [queued_tip.id for queued_tip in queued_tips]

        self.studenttip_set.filter(id__in=queued_tips).update(is_queued=False)
