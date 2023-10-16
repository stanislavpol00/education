class SelectFieldResourceMixin:
    allow_select_fields = "__all__"

    @classmethod
    def get_allow_select_fields(cls):
        all_field_names = list(cls.fields.keys())

        if not cls.allow_select_fields:
            return None

        if cls.allow_select_fields == "__all__":
            return all_field_names

        non_support_fields = ", ".join(
            [
                field
                for field in cls.allow_select_fields
                if field not in all_field_names
            ]
        )
        if non_support_fields:
            raise Exception(
                "These fields is not supported for selecting: "
                f"{non_support_fields}"
            )

        return cls.allow_select_fields

    def __init__(self, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(**kwargs)

    def get_user_selected_fields(self):
        selected_field_names = (
            self.request.POST.getlist("selected_fields") or []
        )
        selected_fields = [
            self.fields[field_name]
            for field_name in selected_field_names
            if field_name in self.fields
        ]
        return selected_fields

    def get_export_fields(self):
        default_fields = super().get_export_fields()
        selected_fields = self.get_user_selected_fields()
        fields = selected_fields if selected_fields else default_fields
        return fields


class SelectFieldExportModelAdminMixin:
    @property
    def allow_select_fields(self):
        get_allow_select_fields = getattr(
            self.resource_class, "get_allow_select_fields", None
        )
        if get_allow_select_fields:
            return get_allow_select_fields()
        return False

    def get_export_resource_kwargs(self, request, *args, **kwargs):
        kwargs_data = super().get_export_resource_kwargs(
            request, *args, **kwargs
        )
        if self.allow_select_fields:
            kwargs_data["request"] = request
        return kwargs_data

    def get_export_context_data(self):
        data = super().get_export_context_data()
        data["allow_select_fields"] = self.allow_select_fields
        return data
