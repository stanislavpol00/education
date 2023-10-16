import re
from copy import deepcopy

from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.utils.html import format_html_join
from django.utils.translation import gettext_lazy as _


class Select2Filter(SimpleListFilter):
    use_select = True
    multiple = False
    placeholder = _("All")
    ajax_url = None
    choices_queryset = None

    default_select_attrs = {
        "style": "width: 100%",
        "class": "select2 admin-filter-select2-search",
    }

    @classmethod
    def clone(cls, class_name=None, **attrs):
        if class_name:
            new_name = class_name
        else:
            new_name = "{}_{}".format(
                cls.__name__, int(timezone.now().timestamp())
            )

        new_name = re.sub(r"_", " ", new_name).title()
        new_name = re.sub(r"\s", "_", new_name)

        return type(new_name, (cls,), attrs)

    @property
    def select_attrs(self):
        attrs = deepcopy(self.default_select_attrs)
        attrs["id"] = self.parameter_name
        attrs["name"] = self.parameter_name
        if self.multiple:
            attrs["multiple"] = "true"
        if self.placeholder:
            attrs["placeholder"] = self.placeholder
        if self.ajax_url:
            attrs["data-ajax--url"] = self.ajax_url
        return attrs

    def select_attrs_to_string(self):
        return format_html_join(
            " ", '{}="{}"', [(k, v) for k, v in self.select_attrs.items()]
        )

    def lookups(self, request, model_admin):
        if self.ajax_url:
            return
        return super().lookups(request, model_admin)

    def has_output(self):
        if self.ajax_url:
            return True
        return super().has_output()

    def choices(self, changelist):
        if self.ajax_url:
            values = self.value_as_list()
            if values and self.choices_queryset:
                queryset = self.choices_queryset.filter(id__in=values)
                for obj in queryset:
                    yield {
                        "selected": True,
                        "value": obj.id,
                        "display": str(obj),
                    }
            return []
        return super().choices(changelist)

    def value_as_list(self):
        values = self.value().split(",") if self.value() else []
        return [int(idx) for idx in values]

    def queryset(self, request, queryset):
        values = self.value_as_list()
        if values:
            queryset = queryset.filter(
                **{f"{self.parameter_name}__in": values}
            )
        return queryset

    def expected_parameters(self):
        if self.multiple:
            return [self.lookup_kwarg, self.lookup_kwarg_isnull]
        return super().expected_parameters()
