from django.db import models
from django.db.models import Avg, F
from django.db.models.functions import Coalesce
from django.utils import timezone


class ExampleRatingQuerySet(models.QuerySet):
    def top_rated(self, days=180, limit=10):
        days_ago = timezone.localtime() - timezone.timedelta(days=days)

        queryset = self.filter(created_at__gte=days_ago)

        queryset = (
            queryset.values("example")
            .annotate(
                clarity_average_rating=Coalesce(Avg("clarity"), 0.0),
                recommended_average_rating=Coalesce(Avg("recommended"), 0.0),
            )
            .annotate(
                average_rating=(
                    F("clarity_average_rating")
                    + F("recommended_average_rating")
                )
                / 2
            )
            .order_by("-average_rating")[:limit]
        )

        return queryset
