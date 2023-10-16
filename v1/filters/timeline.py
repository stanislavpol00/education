import django_filters

from main.models import Timeline


class TimelineFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )

    class Meta:
        model = Timeline
        fields = ["id", "days", "is_default", "name"]
