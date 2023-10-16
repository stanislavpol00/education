import django_filters
from django.db.models import Q

from main.models import Student


class StudentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name=None, method="filter_name")

    tag = django_filters.CharFilter(field_name=None, method="filter_tag")

    caseload_only = django_filters.BooleanFilter(
        field_name=None, method="filter_caseload_only"
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "name",
            "is_active",
            "visible_for_guest",
            "added_by",
        ]

    def filter_name(self, queryset, name, value):
        if value:
            value = value.lower()
            queryset = queryset.filter(
                Q(first_name__icontains=value)
                | Q(last_name__icontains=value)
                | Q(nickname__icontains=value)
            )

        return queryset

    def filter_tag(self, queryset, name, value):
        if value:
            tags = value.split(",")
            queryset = queryset.filter(tags__name__in=tags)

        return queryset

    def filter_caseload_only(self, queryset, name, value):
        if value:
            user = self.request.user
            queryset = queryset.filter(experimental_student__user_id=user.id)

        return queryset
