from dal import autocomplete

from .base_model_select2_mixin import ModelSelect2Mixin


class ModelSelect2(ModelSelect2Mixin, autocomplete.ModelSelect2):
    pass
