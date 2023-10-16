from django_admin_multiple_choice_list_filter.list_filters import (
    MultipleChoiceListFilter,
)

import constants


class LevelListFilter(MultipleChoiceListFilter):
    title = "Level"
    parameter_name = "levels__in"

    def lookups(self, request, model_admin):
        return constants.Levels.CHOICES
