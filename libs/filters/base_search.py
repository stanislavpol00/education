import django_filters


class BaseSearchFilter(django_filters.FilterSet):
    search_fields = django_filters.CharFilter(
        field_name=None, method="filter_nothing"
    )
    search_text = django_filters.CharFilter(
        field_name=None, method="filter_nothing"
    )

    def filter_nothing(self, queryset, name, value):
        return queryset

    def do_search(self, filtered_queryset, search_text, search_fields):
        raise NotImplementedError

    def filter_queryset(self, queryset):
        filtered_queryset = super().filter_queryset(queryset)

        search_text = self.data.get("search_text")
        search_fields = self.data.get("search_fields")
        if search_text:
            if not search_fields:
                search_fields = []
            else:
                search_fields = search_fields.split(",")

            filtered_queryset = self.do_search(
                filtered_queryset, search_text, search_fields
            )

        return filtered_queryset
