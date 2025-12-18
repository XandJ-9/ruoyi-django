from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .core import BaseViewSet
from ..permission import HasRolePermission
from apps.common.mixins import ExportExcelMixin
from collections import OrderedDict
from ..models import Notice
from ..serializers import NoticeSerializer, NoticeQuerySerializer, NoticeUpdateSerializer

class NoticeViewSet(BaseViewSet, ExportExcelMixin):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    update_body_serializer_class = NoticeUpdateSerializer
    update_body_id_field = 'noticeId'
    export_field_label = OrderedDict([
        ('notice_id', '公告ID'),
        ('notice_title', '公告标题'),
        ('notice_type', '公告类型'),
        ('status', '状态'),
        ('create_by', '创建者'),
        ('create_time', '创建时间')
    ])
    export_filename = '通知公告'

    def get_queryset(self):
        queryset = super().get_queryset()
        s = NoticeQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        
        if data.get('noticeTitle'):
            queryset = queryset.filter(notice_title__icontains=data['noticeTitle'])
        if data.get('createBy'):
            queryset = queryset.filter(create_by__icontains=data['createBy'])
        if data.get('noticeType'):
            queryset = queryset.filter(notice_type=data['noticeType'])
            
        return queryset.order_by('-create_time')
