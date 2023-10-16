from django.contrib import admin

from ..models import UserStudentMapping


@admin.register(UserStudentMapping)
class UserStudentMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "user",
        "date_joined",
    )
    list_display_links = ("id",)
