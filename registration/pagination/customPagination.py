from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import LimitOffsetPagination


class customPagination(LimitOffsetPagination):
    default_limit = 2
    max_limit = 2


class customPagePagination(PageNumberPagination):
    page_size = 1
    # page_query_param = 'page_size'
    max_page_size = 1
