from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, Exists, OuterRef, Q
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone

import constants
from libs.querysets import BaseQuerySet


class TipQuerySet(BaseQuerySet):
    DEFAULT_SEARCH_ICONTAINS_FIELDS = {
        "title": "title",
        "description": "description",
        "sub_goal": "sub_goal",
        "example_description": "example__description",
        "tip_summary": "tip_summary",
    }
    DEFAULT_SEARCH_JSON_FIELDS = {
        "child_context": {
            "name": "child_context",
            "values": constants.ChildContext.VALUES,
        },
        "environment_context": {
            "name": "environment_context",
            "values": constants.Environment.VALUES,
        },
    }

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

    def by_dlp(self, user):
        from main.models import StudentTip, TipRating

        queryset = self.filter(
            studenttip__is_queued=False,
            studenttip__student__experimental_student__user_id=user.id,
        )

        tip_ratings = TipRating.objects.filter(
            added_by_id=user.id,
            tip_id=OuterRef("pk"),
            student_id__isnull=True,
            retry_later=True,
        )

        is_rated = Exists(
            tip_ratings.filter(
                clarity__gt=0,
                relevance__gt=0,
                uniqueness__gt=0,
            )
        )
        student_tips = (
            StudentTip.objects.filter(
                tip_id=OuterRef("pk"),
                is_graduated=True,
            )
            .values("tip_id")
            .annotate(graduated_for=ArrayAgg("student_id"))
        )

        queryset = (
            queryset.exclude(
                pk__in=TipRating.objects.filter(
                    retry_later=False, added_by_id=user.id
                ).values_list("tip_id", flat=True)
            )
            .annotate(
                read_count=Coalesce(tip_ratings.values("read_count")[:1], 0),
                try_count=Coalesce(tip_ratings.values("try_count")[:1], 0),
                helpful_count_by_user=Coalesce(
                    tip_ratings.values("helpful_count")[:1], 0
                ),
                is_rated=is_rated,
                graduated_for=Coalesce(
                    student_tips.values("graduated_for")[:1], []
                ),
            )
            .distinct()
        )

        return queryset

    def annotate_count_value(self, user_id):
        from main.models import TipRating

        tip_ratings = TipRating.objects.filter(
            added_by_id=user_id,
            student_id__isnull=True,
            tip_id=OuterRef("pk"),
        )

        is_rated = Exists(
            tip_ratings.filter(
                clarity__gt=0,
                relevance__gt=0,
                uniqueness__gt=0,
            )
        )

        queryset = self.annotate(
            read_count=Coalesce(tip_ratings.values("read_count")[:1], 0),
            try_count=Coalesce(tip_ratings.values("try_count")[:1], 0),
            helpful_count_by_user=Coalesce(
                tip_ratings.values("helpful_count")[:1], 0
            ),
            is_rated=is_rated,
        )

        return queryset
