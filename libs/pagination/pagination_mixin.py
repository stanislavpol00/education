from collections import OrderedDict

from rest_framework.exceptions import NotFound
from rest_framework.response import Response


class PaginationMixin:
    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view=view)
        except NotFound:
            return list()

    def get_paginated_response(self, data):
        if hasattr(self, "page") and self.page is not None:
            return super().get_paginated_response(data)
        else:
            return Response(
                OrderedDict(
                    [
                        ("count", None),
                        ("next", None),
                        ("previous", None),
                        ("results", data),
                    ]
                )
            )
