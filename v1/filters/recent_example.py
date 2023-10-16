import django_filters
from django.db.models import Q
from django.utils import timezone

from main.models import Example


class RecentExampleFilter(django_filters.FilterSet):
    def __init__(self, data, *args, **kwargs):
        if not data.get("days"):
            data = data.copy()
            data["days"] = 7
        super().__init__(data, *args, **kwargs)

    user = django_filters.NumberFilter(method="filter_user")
    days = django_filters.NumberFilter(method="filter_created_at")

    class Meta:
        model = Example
        fields = ["user", "days"]

    def filter_user(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(updated_by_id=value) | Q(added_by_id=value)
            )
        return queryset

    def filter_created_at(self, queryset, name, value):
        days_ago = timezone.localtime() - timezone.timedelta(days=int(value))
        return queryset.filter(created_at__gte=days_ago)
