import django_filters

from main.models import StudentExample


class StudentExampleFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    end_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lt"
    )
    reason = django_filters.CharFilter(
        field_name="reason", lookup_expr="icontains"
    )

    class Meta:
        model = StudentExample
        fields = [
            "example",
            "student",
            "episode",
            "is_active",
            "added_by",
            "start_date",
            "end_date",
            "reason",
        ]
