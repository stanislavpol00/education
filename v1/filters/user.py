import django_filters

from main.models import User


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(
        field_name="username", lookup_expr="icontains"
    )
    email = django_filters.CharFilter(
        field_name="email", lookup_expr="icontains"
    )
    full_name = django_filters.CharFilter(
        field_name="full_name", lookup_expr="icontains"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "full_name",
            "is_active",
            "role",
            "is_team_lead",
        ]
