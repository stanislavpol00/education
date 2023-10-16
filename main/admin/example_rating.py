from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from ..models import ExampleRating


@admin.register(ExampleRating)
class ExampleRatingAdmin(ImportExportModelAdmin):
    list_display = (
        "id",
        "example",
        "added_by",
        "clarity",
        "recommended",
        "comment",
    )
    list_display_links = (
        "example",
        "added_by",
    )
    list_editable = (
        "clarity",
        "recommended",
        "comment",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("added_by", "example")
