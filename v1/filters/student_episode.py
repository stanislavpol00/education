import django_filters

from main.models import Episode
from libs.filters import BaseSearchFilter


class StudentEpisodeFilter(BaseSearchFilter):
    start_date = django_filters.DateTimeFilter(
        field_name="date", lookup_expr="gte"
    )
    end_date = django_filters.DateTimeFilter(
        field_name="date", lookup_expr="lte"
    )
    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains"
    )
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )

    class Meta:
        model = Episode
        fields = [
            "start_date",
            "end_date",
            "title",
            "description",
            "user",
            "is_active",
            "full",
            "landmark",
            "search_text",
            "search_fields",
            "practitioner",
        ]

    def do_search(self, filtered_queryset, search_text, search_fields):
        return Episode.objects.search(
            filtered_queryset, search_text, search_fields
        )
