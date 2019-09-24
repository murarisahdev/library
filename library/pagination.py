from rest_framework import pagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class CustomResultsSetPagination(PageNumberPagination):
    page_size = settings.PAGINATION_PAGE_SIZE
    page_size_query_param = 'page_size'
    
    def get_paginated_response(self, data):

        return Response({
            'data': data,
            'meta': {
                "totalRecords": self.page.paginator.count,
                "page-size": self.page_size,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
        })