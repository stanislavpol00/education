from django.db import models
from django.db.models import Avg, F
from django.db.models.functions import Coalesce
from django.utils import timezone


class TipRatingQuerySet(models.QuerySet):
    def top_rated(self, days=180, limit=10):
        days_ago = timezone.localtime() - timezone.timedelta(days=days)

        queryset = self.filter(created_at__gte=days_ago)

        queryset = (
            queryset.values(
                "tip",
                "tip__title",
                "tip__state",
                "tip__levels",
                "tip__updated_by",
                "tip__added_by",
                "tip__created_at",
            )
            .annotate(
                clarity_average_rating=Coalesce(Avg("clarity"), 0.0),
                relevance_average_rating=Coalesce(Avg("relevance"), 0.0),
                uniqueness_average_rating=Coalesce(Avg("uniqueness"), 0.0),
            )
            .annotate(
                average_rating=(
                    F("clarity_average_rating")
                    + F("relevance_average_rating")
                    + F("uniqueness_average_rating")
                )
                / 3
            )
            .annotate(
                id=F("tip"),
                title=F("tip__title"),
                state=F("tip__state"),
                levels=F("tip__levels"),
                updated_by=F("tip__updated_by"),
                added_by=F("tip__added_by"),
                created_at=F("tip__created_at"),
            )
            .values(
                "id",
                "title",
                "state",
                "levels",
                "updated_by",
                "added_by",
                "created_at",
                "average_rating",
            )
            .order_by("-average_rating")[:limit]
        )

        return queryset

    def get_or_create_with_student(self, user, tip, student):
        if student is None:
            existed = self.filter(
                student__isnull=True, tip=tip, added_by=user
            ).first()
            if existed:
                return existed
            return self.create(tip=tip, added_by=user)
        else:
            instance, _ = self.get_or_create(
                added_by=user, tip=tip, student=student
            )
        return instance

    def get_or_update_read_count(self, user, tip, student=None):
        instance, _ = self.get_or_create(
            added_by=user, tip=tip, student=student
        )

        instance.read_count += 1
        instance.save(update_fields=["read_count"])

        return instance

    def get_or_update_try_count(self, user, tip, student=None):
        instance, _ = self.get_or_create(
            added_by=user, tip=tip, student=student
        )

        instance.try_count += 1
        instance.save(update_fields=["try_count"])

        return instance

    def get_or_update_retry_later(self, user, tip, retry_later, student=None):
        instance, _ = self.get_or_create(
            added_by=user, tip=tip, student=student
        )

        instance.retry_later = retry_later
        instance.save(update_fields=["retry_later"])

    def get_tips_tried(self, user):
        queryset = self.filter(added_by=user, try_count__gt=0)

        return queryset.count()

    def get_read_but_not_rated_tip_ratings(self):
        return self.filter(
            retry_later=True,
            clarity=0,
            relevance=0,
            uniqueness=0,
            read_count__gt=0,
        )
