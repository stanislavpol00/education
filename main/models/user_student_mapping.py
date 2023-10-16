from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..querysets import UserStudentMappingQuerySet


class UserStudentMapping(models.Model):
    objects = UserStudentMappingQuerySet.as_manager()

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        "Student",
        verbose_name=_("Student"),
        related_name="experimental_student",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        related_name="experimental_user",
        on_delete=models.CASCADE,
    )
    date_joined = models.DateTimeField(auto_now_add=True)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = [("student", "user")]

    @cached_property
    def has_assigned_student_yourself(self):
        return self.added_by_id == self.user_id
