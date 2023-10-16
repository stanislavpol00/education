from import_export.admin import ImportExportModelAdmin

from .mixin import ExportFilterSetMixin, SelectFieldExportModelAdminMixin


class BaseImportExportModelAdmin(
    SelectFieldExportModelAdminMixin,
    ExportFilterSetMixin,
    ImportExportModelAdmin,
):
    export_template_name = "import_export/export.html"
