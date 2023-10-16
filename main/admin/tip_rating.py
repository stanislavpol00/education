from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from libs.import_export import BaseImportExportModelAdmin
from libs.import_export.resources import TipRatingResource

from ..models import TipRating
from .filters import TipRatingExportFilterset


@admin.register(TipRating)
class TipRatingAdmin(BaseImportExportModelAdmin):
    list_display = (
        "id",
        "tip",
        "added_by",
        "clarity",
        "relevance",
        "uniqueness",
        "comment",
        "commented_at",
        "read_count",
        "try_count",
        "try_comment",
        "tried_at",
        "retry_later",
        "helpful_count",
    )
    list_display_links = (
        "tip",
        "added_by",
    )
    list_editable = (
        "clarity",
        "relevance",
        "uniqueness",
        "comment",
        "commented_at",
        "read_count",
        "try_count",
        "try_comment",
        "tried_at",
        "retry_later",
        "helpful_count",
    )

    list_filter = (
        "added_by__role",
        ("created_at", DateRangeFilter),
        ("updated_at", DateRangeFilter),
        ("commented_at", DateRangeFilter),
        ("tried_at", DateRangeFilter),
    )

    resource_class = TipRatingResource
    export_filterset_class = TipRatingExportFilterset

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("tip", "added_by")
