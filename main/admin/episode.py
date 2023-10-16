from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from ..models import Episode
from .filters import StudentSelect2Filter, TagSelect2Filter, UserSelect2Filter


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "user",
        "title",
        "description",
        "is_active",
        "date",
        "tag_list",
    )
    list_display_links = (
        "student",
        "user",
    )
    list_editable = ("title", "description", "is_active", "date")

    list_filter = (
        StudentSelect2Filter,
        UserSelect2Filter,
        ("created_at", DateRangeFilter),
        ("date", DateRangeFilter),
        TagSelect2Filter,
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("student", "user").prefetch_related(
            "tags"
        )

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
