from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter
from reversion_compare.admin import CompareVersionAdmin

from ..models import Example
from .filters import (
    EpisodeSelect2Filter,
    ExampleTypeListFilter,
    TagSelect2Filter,
    TipSelect2Filter,
    UserSelect2Filter,
)


@admin.register(Example)
class ExampleAdmin(ImportExportModelAdmin, CompareVersionAdmin):
    list_display = (
        "id",
        "tip",
        "description",
        "added_by",
        "updated_by",
        "updated_at",
        "tag_list",
    )
    list_display_links = ("id", "tip", "updated_by")
    list_editable = ("description",)

    list_filter = (
        UserSelect2Filter.clone(
            title=_("Added By"), parameter_name="added_by"
        ),
        TipSelect2Filter,
        EpisodeSelect2Filter,
        ExampleTypeListFilter,
        ("created_at", DateRangeFilter),
        TagSelect2Filter,
        "is_bookmarked",
    )
    search_fields = ("description", "tip__title")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("tip", "updated_by").prefetch_related(
            "tags"
        )

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
