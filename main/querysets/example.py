from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from libs.querysets import BaseQuerySet


class ExampleQuerySet(BaseQuerySet):
    def contributions(self, days=91, user_id=None):
        queryset = self

        days_ago = timezone.localtime() - timezone.timedelta(days=days)
        queryset = queryset.filter(created_at__gte=days_ago)

        queryset = (
            queryset.annotate(date=TruncDate("created_at"))
            .values("date", "added_by")
            .annotate(count=Count("id"))
            .order_by(
                "-date",
                "-count",
                "added_by",
            )
        )

        if user_id:
            queryset = queryset.filter(added_by=user_id)

        return queryset

    def by_user_id(self, user_id):
        queryset = self.filter(
            Q(updated_by_id=user_id) | Q(added_by_id=user_id)
        )

        return queryset

    def filter_by_params(self, **kwargs):
        queryset = self

        if kwargs.get("start_date"):
            queryset = queryset.filter(created_at__gte=kwargs["start_date"])

        if kwargs.get("end_date"):
            queryset = queryset.filter(created_at__lt=kwargs["end_date"])

        queryset = queryset.order_by("-updated_at")

        return queryset
