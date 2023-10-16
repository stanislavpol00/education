from django.contrib import admin

from ..models import StudentTip


@admin.register(StudentTip)
class StudentTipAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "tip",
        "added_by",
        "is_graduated",
    )
    list_display_links = ("student", "tip", "added_by")
    list_editable = ("is_graduated",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("tip", "student", "added_by")
