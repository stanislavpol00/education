from functools import reduce
from operator import and_, or_

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models


class BaseModelAutocompleteView(
    LoginRequiredMixin, autocomplete.Select2QuerySetView
):
    model = None
    search_fields = []
    forward_fields = []
    paginate_by = 20

    def get_queryset(self):
        q_obj = self.get_query_object()
        queryset = self.model.objects.filter(q_obj)

        return queryset

    def get_query_object(self):
        q_definitions = []
        if self.q:
            q_definitions = [
                {f"{field}__icontains": self.q} for field in self.search_fields
            ]

        forwared_q_definitions = []
        for forward_field, value in self.forwarded.items():
            has_forward_field = forward_field in self.forward_fields
            if not (has_forward_field and value):
                continue
            forwared_q_definitions.append({forward_field: value})

        q_obj = models.Q()
        if q_definitions:
            q_obj |= reduce(
                or_,
                [models.Q(**definition) for definition in q_definitions],
            )
        if forwared_q_definitions:
            q_obj &= reduce(
                and_,
                [
                    models.Q(**definition)
                    for definition in forwared_q_definitions
                ],
            )

        return q_obj
