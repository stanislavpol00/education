import django_filters

from main.models import Example


class EpisodeExampleFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )

    class Meta:
        model = Example
        fields = ["tip", "updated_by", "description", "is_active"]
