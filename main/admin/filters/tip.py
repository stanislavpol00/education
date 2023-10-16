import django_filters
from django.db import models
from django.forms import SplitDateTimeWidget
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from main.models import Tip, TipRating
from libs.filters import Select2Filter


class TipExportFilterset(django_filters.FilterSet):
    is_read = django_filters.BooleanFilter(
        label=_("Is Read?"),
        method="filter_is_read",
    )
    is_rating = django_filters.BooleanFilter(
        label=_("Is Rating?"),
        method="filter_is_rating",
    )
    tried = django_filters.BooleanFilter(
        label=_("Tried?"),
        method="filter_tried",
    )
    created = django_filters.DateTimeFromToRangeFilter(
        field_name="created_at",
        widget=SplitDateTimeWidget(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Tip
        fields = ["is_read", "is_rating", "tried", "created"]

    def filter_is_read(self, queryset, name, value):
        if value is None:
            return queryset

        exists_subquery = models.Exists(
            TipRating.objects.filter(
                tip=models.OuterRef("id"),
                read_count__gt=0,
            )
        )

        if value:
            return queryset.filter(exists_subquery)
        return queryset.filter(~exists_subquery)

    def filter_is_rating(self, queryset, name, value):
        if value is None:
            return queryset

        exists_subquery = models.Exists(
            TipRating.objects.filter(
                models.Q(clarity__gt=0)
                | models.Q(relevance__gt=0)
                | models.Q(uniqueness__gt=0),
                tip=models.OuterRef("id"),
            )
        )

        if value:
            return queryset.filter(exists_subquery)
        return queryset.filter(~exists_subquery)

    def filter_tried(self, queryset, name, value):
        if value is None:
            return queryset

        exists_subquery = models.Exists(
            TipRating.objects.filter(
                tip=models.OuterRef("id"), try_count__gt=0
            )
        )

        if value:
            return queryset.filter(exists_subquery)
        return queryset.filter(~exists_subquery)


class TipSelect2Filter(Select2Filter):
    title = _("Tip")
    parameter_name = "tip"
    ajax_url = reverse_lazy("autocomplete:tip")
    choices_queryset = Tip.objects.all()
