from django.utils.translation import gettext_lazy as _


class ModelSelect2Mixin:
    def __init__(self, placeholder=None, *args, **kwargs):
        minimum_input_length = kwargs.pop("minimum_input_length")

        super().__init__(*args, **kwargs)

        if not placeholder:
            placeholder = _("All")

        if minimum_input_length:
            self.attrs["data-minimum-input-length"] = minimum_input_length

        self.attrs.update(
            {
                "data-placeholder": placeholder,
                "data-allow-clear": "true",
                "data-ajax--delay": 100,
                "data-ajax--cache": "true",
            }
        )
