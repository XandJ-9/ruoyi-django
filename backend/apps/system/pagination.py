from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_query_param = 'pageNum'
    page_size_query_param = 'pageSize'
    max_page_size = 100
    def get_paginated_response(self, data):
        return Response({'code': 200, 'msg': '操作成功', 'total': self.page.paginator.count, 'rows': data})