from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .core import BaseViewSet
from ..permission import HasRolePermission
from ..models import Notice
from ..serializers import NoticeSerializer, NoticeQuerySerializer, NoticeUpdateSerializer

class NoticeViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    update_body_serializer_class = NoticeUpdateSerializer
    update_body_id_field = 'noticeId'

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
