from django.db.models import Case, Exists, OuterRef, Value, When
from django.db.models.functions import Coalesce

import constants
from libs.querysets import BaseQuerySet


class StudentTipQuerySet(BaseQuerySet):
    DEFAULT_SEARCH_ICONTAINS_FIELDS = {
        "title": "tip__title",
        "description": "tip__description",
        "sub_goal": "tip__sub_goal",
        "example_description": "tip__example__description",
        "tip_summary": "tip__tip_summary",
    }
    DEFAULT_SEARCH_JSON_FIELDS = {
        "child_context": {
            "name": "tip__child_context",
            "values": constants.ChildContext.VALUES,
        },
        "environment_context": {
            "name": "tip__environment_context",
            "values": constants.Environment.VALUES,
        },
    }

    def annotate_browse_tips(self, user, student_id):
        from main.models import Example, TipRating

        queryset = self

        tip_ratings = TipRating.objects.filter(
            added_by_id=user.id,
            tip_id=OuterRef("tip_id"),
            student_id=OuterRef("student_id"),
            retry_later=True,
        )

        # is_read
        is_read = Exists(tip_ratings.filter(read_count__gt=0))
        # is_rated
        is_rated = Exists(
            TipRating.objects.filter(
                added_by_id=user.id,
                student_id=student_id,
                tip_id=OuterRef("tip_id"),
                retry_later=True,
                clarity__gt=0,
                relevance__gt=0,
                uniqueness__gt=0,
            )
        )

        queryset = queryset.annotate(
            read_count=Coalesce(tip_ratings.values("read_count")[:1], 0),
            try_count=Coalesce(tip_ratings.values("try_count")[:1], 0),
            helpful_count=Coalesce(tip_ratings.values("helpful_count")[:1], 0),
            is_read=is_read,
            is_rated=is_rated,
        )

        # has_new_info
        existed_example = Example.objects.filter(tip_id=OuterRef("tip_id"))
        queryset = (
            queryset.annotate(is_existed_example=Exists(existed_example))
            .annotate(
                has_new_info=Case(
                    When(
                        is_read=False,
                        is_existed_example=True,
                        then=Value(True),
                    ),
                    default=Value(False),
                )
            )
            .filter(student_id=student_id)
        )

        queryset = queryset.distinct()

        return queryset

    def by_dlp(self, user_id):
        return self.filter(student__experimental_student__user_id=user_id)
