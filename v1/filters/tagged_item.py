import django_filters
from taggit.models import TaggedItem


class TaggedItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="tag__name", lookup_expr="icontains"
    )
    slug = django_filters.CharFilter(
        field_name="tag__slug", lookup_expr="icontains"
    )

    class Meta:
        model = TaggedItem
        fields = [
            "name",
            "tag",
            "object_id",
            "content_type",
        ]
