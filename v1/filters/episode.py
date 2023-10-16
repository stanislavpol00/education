import django_filters

from main.models import Episode


class EpisodeFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(
        field_name="date", lookup_expr="gte"
    )
    end_date = django_filters.DateTimeFilter(
        field_name="date", lookup_expr="lte"
    )
    breaking = django_filters.BooleanFilter(
        field_name="full", method="filter_breaking"
    )
    only_mine = django_filters.BooleanFilter(
        field_name="user", method="filter_only_mine"
    )

    tag = django_filters.CharFilter(field_name=None, method="filter_tag")

    class Meta:
        model = Episode
        fields = [
            "start_date",
            "end_date",
            "breaking",
            "only_mine",
            "student",
            "practitioner",
        ]

    def filter_only_mine(self, queryset, name, value):
        if value:
            return queryset.filter(user=self.request.user)
        return queryset

    def filter_breaking(self, queryset, name, value):
        if value:
            return queryset.filter(full=False)
        return queryset.filter(full=True)

    def filter_tag(self, queryset, name, value):
        if value:
            tags = value.split(",")
            queryset = queryset.filter(tags__name__in=tags)

        return queryset
