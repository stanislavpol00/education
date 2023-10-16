from django.contrib import admin

from ..models import RoleAssignment


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "group",
        "organization",
    )
    list_display_links = (
        "user",
        "group",
        "organization",
    )
