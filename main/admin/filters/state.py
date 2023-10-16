from django_admin_multiple_choice_list_filter.list_filters import (
    MultipleChoiceListFilter,
)

import constants


class StateListFilter(MultipleChoiceListFilter):
    title = "State"
    parameter_name = "state__in"

    def lookups(self, request, model_admin):
        return constants.States.CHOICES
