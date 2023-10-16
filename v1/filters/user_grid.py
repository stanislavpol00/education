import django_filters

from main.models import User


class UserGridFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(
        field_name="full_name", lookup_expr="icontains"
    )

    class Meta:
        model = User
        fields = [
            "full_name",
            "role",
        ]
