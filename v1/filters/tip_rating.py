import django_filters

from main.models import TipRating


class TipRatingFilter(django_filters.FilterSet):
    clarity_from = django_filters.NumberFilter(
        field_name="clarity", lookup_expr="gte"
    )
    clarity_to = django_filters.NumberFilter(
        field_name="clarity", lookup_expr="lte"
    )
    relevance_from = django_filters.NumberFilter(
        field_name="relevance", lookup_expr="gte"
    )
    relevance_to = django_filters.NumberFilter(
        field_name="relevance", lookup_expr="lte"
    )
    uniqueness_from = django_filters.NumberFilter(
        field_name="uniqueness", lookup_expr="gte"
    )
    uniqueness_to = django_filters.NumberFilter(
        field_name="uniqueness", lookup_expr="lte"
    )
    start_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    end_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lt"
    )

    class Meta:
        model = TipRating
        fields = [
            "added_by",
            "clarity_from",
            "clarity_to",
            "relevance_from",
            "relevance_to",
            "uniqueness_from",
            "uniqueness_to",
            "start_date",
            "end_date",
            "student",
        ]
