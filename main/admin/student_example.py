from django.contrib import admin

from ..models import StudentExample


@admin.register(StudentExample)
class StudentExampleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reason",
        "student",
        "example",
        "episode",
        "added_by",
        "added",
    )
    list_display_links = ("student", "example", "episode", "added_by")
    list_editable = ("reason",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "example", "student", "added_by", "episode"
        )
