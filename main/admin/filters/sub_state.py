from django_admin_multiple_choice_list_filter.list_filters import (
    MultipleChoiceListFilter,
)

import constants


class SubStateListFilter(MultipleChoiceListFilter):
    title = "Sub state"
    parameter_name = "substate__in"

    def lookups(self, request, model_admin):
        return constants.SubStates.CHOICES
