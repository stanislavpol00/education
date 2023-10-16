import django_filters
from taggit.models import Tag


class TagFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )
    slug = django_filters.CharFilter(
        field_name="slug", lookup_expr="icontains"
    )

    class Meta:
        model = Tag
        fields = [
            "name",
            "slug",
        ]
