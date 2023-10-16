from django.db import models


class StudentQuerySet(models.QuerySet):
    def to_dict(self, student_ids=None):
        queryset = self

        if student_ids:
            queryset = queryset.filter(pk__in=student_ids)

        items = {}
        for item in queryset:
            items[item.id] = item

        return items
