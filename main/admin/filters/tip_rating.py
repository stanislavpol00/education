import django_filters
from django.forms import SplitDateTimeWidget
from django.utils.translation import gettext_lazy as _

from main.models import TipRating


class TipRatingExportFilterset(django_filters.FilterSet):
    new_comment_first = django_filters.BooleanFilter(
        label=_("New comment first?"),
        method="filter_new_comment_first",
    )
    created = django_filters.DateTimeFromToRangeFilter(
        field_name="created_at",
        widget=SplitDateTimeWidget(attrs={"type": "datetime-local"}),
    )
    commented = django_filters.DateTimeFromToRangeFilter(
        field_name="commented_at",
        widget=SplitDateTimeWidget(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = TipRating
        fields = ["new_comment_first", "created", "commented"]

    def filter_new_comment_first(self, queryset, name, value):
        if value is None:
            return queryset

        if value:
            return queryset.order_by("-commented_at")
        return queryset.order_by("commented_at")
