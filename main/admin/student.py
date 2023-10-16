from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter

from ..models import Student
from .filters import TagSelect2Filter, UserSelect2Filter


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "nickname",
        "is_active",
        "visible_for_guest",
        "image",
        "created_at",
        "tag_list",
    )
    list_display_links = None
    list_editable = (
        "first_name",
        "last_name",
        "nickname",
        "is_active",
        "visible_for_guest",
        "image",
    )

    list_filter = (
        UserSelect2Filter.clone(
            title=_("Added By"),
            parameter_name="added_by",
        ),
        "is_active",
        ("created_at", DateRangeFilter),
        TagSelect2Filter,
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("tags")

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
