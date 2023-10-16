from dal import autocomplete

from .base_model_select2_mixin import ModelSelect2Mixin


class ModelSelect2Multiple(
    ModelSelect2Mixin, autocomplete.ModelSelect2Multiple
):
    pass
