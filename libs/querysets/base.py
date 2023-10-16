from functools import reduce
from operator import and_, or_

from django.db import models
from django.db.models import Count, Q
from django.utils import timezone


class BaseQuerySet(models.QuerySet):
    DEFAULT_SEARCH_ICONTAINS_FIELDS = {}
    DEFAULT_SEARCH_JSON_FIELDS = {}

    def _join_q_objects(self, q_objects, operator):
        if not q_objects:
            return Q()
        return reduce(operator, q_objects)

    def _join_or_q_objects(self, q_objects):
        return self._join_q_objects(q_objects, or_)

    def _join_and_q_objects(self, q_objects):
        return self._join_q_objects(q_objects, and_)

    def search(self, queryset, search_text, search_fields):
        if not queryset:
            queryset = self

        if not search_text:
            return queryset

        if not search_fields:
            search_fields = list(
                self.DEFAULT_SEARCH_ICONTAINS_FIELDS.keys()
            ) + list(self.DEFAULT_SEARCH_JSON_FIELDS.keys())

        icontains_fields = set(search_fields).intersection(
            set(self.DEFAULT_SEARCH_ICONTAINS_FIELDS.keys())
        )
        q_objects = []
        q_objects.extend(
            self.build_icontains_fields_q_objects(
                icontains_fields, search_text
            )
        )

        json_fields = set(search_fields).intersection(
            set(self.DEFAULT_SEARCH_JSON_FIELDS.keys())
        )
        for json_field in json_fields:
            q_objects.extend(
                self.build_json_field_q_object(json_field, search_text)
            )

        q_query_filter = self._join_or_q_objects(q_objects)
        queryset = queryset.filter(q_query_filter)

        return queryset

    def build_icontains_fields_q_objects(self, icontains_fields, search_text):
        q_objects = []
        words = search_text.split()
        for field in icontains_fields:
            field_q_objects = []
            for word in words:
                field_name = self.DEFAULT_SEARCH_ICONTAINS_FIELDS[field]
                field_name_filter = "{0}__icontains".format(field_name)
                field_q_objects.append(Q(**{field_name_filter: word}))

            field_q_objects = self._join_and_q_objects(field_q_objects)

            q_objects.append(field_q_objects)

        return q_objects

    def build_json_field_q_object(self, json_field, search_text):
        q_objects = []
        field_name = self.DEFAULT_SEARCH_JSON_FIELDS[json_field]["name"]
        values = self.DEFAULT_SEARCH_JSON_FIELDS[json_field]["values"]
        words = search_text.split()
        for value in values:
            value_q_objects = []
            for word in words:
                field_name_filter = "{}__{}__icontains".format(
                    field_name, value
                )
                value_q_objects.append(Q(**{field_name_filter: word}))

            value_q_objects = self._join_and_q_objects(value_q_objects)

            q_objects.append(value_q_objects)

        return q_objects

    def to_dict(self, ids, select_related=None, prefetch_related=None):
        queryset = self

        if not ids:
            return queryset.none()

        queryset = queryset.filter(id__in=ids)

        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        items = {}
        for item in queryset:
            items[item.id] = item

        return items

    def annotate_contributed_at(
        self, activities, select_related=None, prefetch_related=None
    ):
        if not activities:
            return self.none()

        ids = set().union(*(activity.keys() for activity in activities))

        items = self.to_dict(ids, select_related, prefetch_related)
        for _, item in items.items():
            for activity in activities:
                if item.id not in activity:
                    continue
                item.contributed_at = activity[item.id]

        return dict(
            sorted(
                items.items(), key=lambda x: x[1].contributed_at, reverse=True
            )
        )

    def count_by_days(self, days=7):
        from_date = timezone.localtime() - timezone.timedelta(days=days)
        to_date = timezone.localtime()

        queryset = (
            self.filter(created_at__gte=from_date, created_at__lt=to_date)
            .values("student_id")
            .annotate(count=Count("student_id"))
        )

        items = {}
        for item in queryset:
            items[item["student_id"]] = item["count"]

        return items
