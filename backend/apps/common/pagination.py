from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_query_param = 'pageNum'
    page_size_query_param = 'pageSize'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = int(request.query_params.get(self.page_size_query_param, self.page_size))
        # 判断是否传入分页的参数
        if request.query_params.get(self.page_query_param, None) or request.query_params.get(self.page_size_query_param, None):
            return super().paginate_queryset(queryset, request, view)
        else:
            return None

    def get_paginated_response(self, data):
        return Response({'code': 200, 'msg': '操作成功', 'total': self.page.paginator.count, 'pageNum': self.page.number, 'pageSize': self.page.paginator.per_page, 'rows': data})
