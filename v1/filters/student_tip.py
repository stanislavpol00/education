import django_filters
from django.db.models import Q

from main.models import StudentTip
from libs.filters import BaseSearchFilter


class StudentTipFilter(BaseSearchFilter):
    start_date = django_filters.DateTimeFilter(method="filter_nothing")
    end_date = django_filters.DateTimeFilter(method="filter_nothing")
    title = django_filters.CharFilter(
        field_name="tip__title", lookup_expr="icontains"
    )
    description = django_filters.CharFilter(
        field_name="tip__description", lookup_expr="icontains"
    )

    class Meta:
        model = StudentTip
        fields = [
            "id",
            "tip",
            "added_by",
            "title",
            "description",
            "start_date",
            "end_date",
            "search_text",
            "search_fields",
            "is_queued",
        ]

    def do_search(self, filtered_queryset, search_text, search_fields):
        return StudentTip.objects.search(
            filtered_queryset, search_text, search_fields
        )

    def filter_queryset(self, queryset):
        filtered_queryset = super().filter_queryset(queryset)

        start_date = self.data.get("start_date")
        end_date = self.data.get("end_date")

        if start_date and end_date is None:
            filtered_queryset = filtered_queryset.filter(
                Q(created_at__gte=start_date)
                | Q(last_used_at__gte=start_date)
                | Q(last_suggested_at__gte=start_date)
            )
        elif start_date is None and end_date:
            filtered_queryset = filtered_queryset.filter(
                Q(created_at__lt=end_date)
                | Q(last_used_at__lt=end_date)
                | Q(last_suggested_at__lt=end_date)
            )
        elif start_date and end_date:
            filtered_queryset = filtered_queryset.filter(
                Q(created_at__gte=start_date, created_at__lt=end_date)
                | Q(last_used_at__gte=start_date, last_used_at__lt=end_date)
                | Q(
                    last_suggested_at__gte=start_date,
                    last_suggested_at__lt=end_date,
                )
            )

        return filtered_queryset
