from django_admin_multiple_choice_list_filter.list_filters import (
    MultipleChoiceListFilter,
)

import constants


class ExampleTypeListFilter(MultipleChoiceListFilter):
    title = "Example type"
    parameter_name = "example_type__in"

    def lookups(self, request, model_admin):
        return constants.ExampleType.CHOICES
