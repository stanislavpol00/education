from rest_framework.pagination import PageNumberPagination

from libs.pagination import PaginationMixin


class LargeResultsSetPagination(PaginationMixin, PageNumberPagination):
    page_size = 1000
    page_size_query_param = "page_size"
    max_page_size = 10000


class StandardResultsSetPagination(PaginationMixin, PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 10000


class SmallResultsSetPagination(PaginationMixin, PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10000
