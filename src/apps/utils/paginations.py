from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.views import APIView


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(
        self,
        queryset: Any,
        request: Request,
        view: APIView | None = None,
    ):
        if "page" in request.query_params:
            return super().paginate_queryset(queryset, request, view)
        return None
