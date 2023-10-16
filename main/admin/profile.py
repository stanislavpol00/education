from django.contrib import admin

from ..models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ("id", "user", "photo")
    list_editable = ("photo",)
