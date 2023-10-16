import django_filters

from main.models import Tip
from libs.filters import BaseSearchFilter


class TipFilter(BaseSearchFilter):
    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains"
    )
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )
    linked_tip = django_filters.NumberFilter(
        field_name=None, method="filter_linked_tip"
    )

    student = django_filters.NumberFilter(
        field_name=None, method="filter_student"
    )
    graduated_for = django_filters.CharFilter(
        field_name=None, method="filter_graduated_for"
    )

    user = django_filters.NumberFilter(
        field_name=None, method="filter_nothing"
    )
    is_queued = django_filters.BooleanFilter(
        field_name=None, method="filter_nothing"
    )

    tag = django_filters.CharFilter(field_name=None, method="filter_tag")

    class Meta:
        model = Tip
        fields = [
            "updated_by",
            "title",
            "description",
            "search_fields",
            "search_text",
            "marked_for_editing",
            "student",
            "graduated_for",
        ]

    def do_search(self, filtered_queryset, search_text, search_fields):
        return Tip.objects.search(
            filtered_queryset, search_text, search_fields
        ).distinct()

    def filter_linked_tip(self, queryset, name, value):
        if value:
            return queryset.filter(linked_tips__id=value)
        return queryset

    def filter_graduated_for(self, queryset, name, value):
        if value:
            graduated_student_ids = value.split(",")
            queryset = queryset.filter(
                studenttip__student_id__in=graduated_student_ids,
                studenttip__is_graduated=True,
            )

        return queryset

    def filter_tag(self, queryset, name, value):
        if value:
            tags = value.split(",")
            queryset = queryset.filter(tags__name__in=tags)

        return queryset

    def filter_student(self, queryset, name, value):
        if value:
            user = self.request.user
            if user.is_dlp:
                queryset = queryset.filter(
                    studenttip__student__experimental_student__student_id=value
                )
            else:
                queryset = queryset.filter(studenttip__student_id=value)

        return queryset

    def filter_queryset(self, queryset):
        filtered_queryset = super().filter_queryset(queryset)

        student = self.data.get("student")
        is_queued = self.data.get("is_queued")
        if student and is_queued is not None:
            filtered_queryset = filtered_queryset.filter(
                studenttip__is_queued=is_queued
            )

        return filtered_queryset.distinct()
