from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from ..models import Activity


@admin.register(Activity)
class ActivityAdmin(ImportExportModelAdmin):
    list_display = (
        "id",
        "type",
        "user",
        "meta",
    )
    list_display_links = ("user",)
