from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.resources import ModelResource
from rangefilter.filter import DateRangeFilter
from reversion_compare.admin import CompareVersionAdmin

from libs.import_export import BaseImportExportModelAdmin
from libs.import_export.mixin import SelectFieldResourceMixin

from ..models import Tip
from .filters import (
    LevelListFilter,
    StateListFilter,
    SubStateListFilter,
    TagSelect2Filter,
    TipExportFilterset,
    UserSelect2Filter,
)


class TipResource(SelectFieldResourceMixin, ModelResource):
    class Meta:
        model = Tip


@admin.register(Tip)
class TipAdmin(
    BaseImportExportModelAdmin,
    CompareVersionAdmin,
):
    list_display = (
        "id",
        "state",
        "substate",
        "levels",
        "title",
        "description",
        "updated_by",
        "created_at",
        "updated_at",
        "tag_list",
        "tip_summary",
    )
    list_display_links = (
        "id",
        "updated_by",
    )
    list_editable = ("state", "substate", "levels", "title", "description")

    list_filter = (
        UserSelect2Filter.clone(
            title=_("Added By"),
            parameter_name="added_by",
        ),
        UserSelect2Filter.clone(
            title=_("Updated By"), parameter_name="updated_by"
        ),
        StateListFilter,
        SubStateListFilter,
        LevelListFilter,
        ("created_at", DateRangeFilter),
        TagSelect2Filter,
    )

    resource_class = TipResource
    export_filterset_class = TipExportFilterset

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("updated_by").prefetch_related("tags")

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
