from rest_framework import viewsets

from ..pagination import (
    LargeResultsSetPagination,
    StandardResultsSetPagination,
)


class BaseStandardPaginationViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination


class BaseLargePaginationViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination


class BaseStandardPaginationReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = StandardResultsSetPagination
