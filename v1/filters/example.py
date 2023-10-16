import django_filters

from main.models import Example


class ExampleFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )

    tag = django_filters.CharFilter(field_name=None, method="filter_tag")

    class Meta:
        model = Example
        fields = ["tip", "updated_by", "episode", "description", "is_active"]

    def filter_tag(self, queryset, name, value):
        if value:
            tags = value.split(",")
            queryset = queryset.filter(tags__name__in=tags)

        return queryset
