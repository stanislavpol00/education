import django_filters
from django.db.models import Prefetch
from django.utils import timezone

from main.models import Episode, Example, Student, Tip


class StudentActivitiesFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(
        field_name=None, method="filter_nothing"
    )
    end_date = django_filters.DateTimeFilter(
        field_name=None, method="filter_nothing"
    )

    class Meta:
        model = Student
        fields = ["start_date", "end_date"]

    def filter_nothing(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        start_date = self.data.get(
            "start_date",
            timezone.localtime() - timezone.timedelta(days=30),
        )
        end_date = self.data.get("end_date", None)

        tips = Tip.objects.filter(updated_at__gte=start_date)
        examples = Example.objects.filter(updated_at__gte=start_date)
        episodes = Episode.objects.filter(
            updated_at__gte=start_date
        ).select_related("user")

        if end_date:
            tips = tips.filter(updated_at__lt=end_date)
            examples = examples.filter(updated_at__lt=end_date)
            episodes = episodes.filter(updated_at__lt=end_date)

        filtered_queryset = queryset.prefetch_related(
            Prefetch("tips", queryset=tips),
            Prefetch("examples", queryset=examples),
            Prefetch("episode_set", queryset=episodes),
        )

        return filtered_queryset
