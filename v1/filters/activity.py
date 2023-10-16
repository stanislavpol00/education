import django_filters
from django.db.models import Value
from django.db.models.functions import Concat

from main.models import Activity


class ActivityFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(
        field_name="user_id", lookup_expr="exact"
    )
    query = django_filters.CharFilter(method="filter_query")
    start_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    end_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    types = django_filters.CharFilter(method="filter_types")

    class Meta:
        model = Activity
        fields = [
            "user",
            "query",
            "start_date",
            "end_date",
        ]

    def filter_query(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(
                full_name=Concat(
                    "user__first_name", Value(" "), "user__last_name"
                )
            ).filter(full_name__icontains=value)
        return queryset

    def filter_types(self, queryset, name, value):
        if value:
            values = value.split(",")
            queryset = queryset.filter(type__in=values)
        return queryset
