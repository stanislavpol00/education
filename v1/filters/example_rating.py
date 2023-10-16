import django_filters

from main.models import ExampleRating


class ExampleRatingFilter(django_filters.FilterSet):
    clarity_from = django_filters.NumberFilter(
        field_name="clarity", lookup_expr="gte"
    )
    clarity_to = django_filters.NumberFilter(
        field_name="clarity", lookup_expr="lte"
    )
    recommended_from = django_filters.NumberFilter(
        field_name="recommended", lookup_expr="gte"
    )
    recommended_to = django_filters.NumberFilter(
        field_name="recommended", lookup_expr="lte"
    )
    start_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    end_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lt"
    )

    class Meta:
        model = ExampleRating
        fields = [
            "added_by",
            "clarity_from",
            "clarity_to",
            "recommended_from",
            "recommended_to",
            "start_date",
            "end_date",
        ]
