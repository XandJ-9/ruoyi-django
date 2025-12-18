from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .core import BaseViewSet
from ..permission import HasRolePermission
from apps.common.mixins import ExportExcelMixin
from collections import OrderedDict
from ..models import Post
from ..serializers import PostSerializer, PaginationQuerySerializer, PostQuerySerializer, PostUpdateSerializer



class PostViewSet(BaseViewSet, ExportExcelMixin):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    update_body_serializer_class = PostUpdateSerializer
    update_body_id_field = 'post_id'
    export_field_label = OrderedDict([
        ('post_code', '岗位编码'),
        ('post_name', '岗位名称'),
        ('post_sort', '岗位排序'),
        ('status', '状态'),
        ('create_time', '创建时间')
    ])
    export_filename = '岗位数据'

    def get_queryset(self):
        queryset = super().get_queryset()
        s = PostQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        
        if data.get('postCode'):
            queryset = queryset.filter(post_code__icontains=data['postCode'])
        if data.get('postName'):
            queryset = queryset.filter(post_name__icontains=data['postName'])
        if data.get('status'):
            queryset = queryset.filter(status=data['status'])
            
        return queryset.order_by('post_sort')
