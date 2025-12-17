from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .core import BaseViewSet
from ..permission import HasRolePermission
from ..models import Notice
from ..serializers import BaseModelSerializer, PaginationQuerySerializer

class NoticeSerializer(BaseModelSerializer):
    noticeId = serializers.IntegerField(source='notice_id', read_only=True)
    noticeTitle = serializers.CharField(source='notice_title')
    noticeType = serializers.CharField(source='notice_type')
    noticeContent = serializers.CharField(source='notice_content', allow_blank=True, required=False)
    
    class Meta:
        model = Notice
        fields = ['noticeId', 'noticeTitle', 'noticeType', 'noticeContent', 'status', 'remark', 'createBy', 'createTime']

class NoticeQuerySerializer(PaginationQuerySerializer):
    noticeTitle = serializers.CharField(required=False, allow_blank=True)
    createBy = serializers.CharField(required=False, allow_blank=True)
    noticeType = serializers.CharField(required=False, allow_blank=True)

class NoticeViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    update_body_serializer_class = NoticeSerializer

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
