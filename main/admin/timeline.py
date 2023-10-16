from django.contrib import admin

from ..models import Timeline


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_default", "days")
    list_display_links = ("name", "is_default", "days")
