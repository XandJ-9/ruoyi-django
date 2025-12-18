from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.system.views.core import BaseViewSet
from apps.system.permission import HasRolePermission
from apps.common.mixins import ExportExcelMixin
from collections import OrderedDict
from .models import OperLog, Logininfor
from .serializers import (
    OperLogSerializer, OperLogQuerySerializer,
    LogininforSerializer, LogininforQuerySerializer
)

class OperLogViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = OperLog.objects.all()
    serializer_class = OperLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        s = OperLogQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        
        if data.get('title'):
            queryset = queryset.filter(title__icontains=data['title'])
        if data.get('operName'):
            queryset = queryset.filter(oper_name__icontains=data['operName'])
        if data.get('businessType') is not None:
            queryset = queryset.filter(business_type=data['businessType'])
        if data.get('status') is not None:
            queryset = queryset.filter(status=data['status'])
        if data.get('beginTime'):
            queryset = queryset.filter(oper_time__gte=data['beginTime'])
        if data.get('endTime'):
            queryset = queryset.filter(oper_time__lte=data['endTime'])
            
        return queryset.order_by('-oper_time')

    @action(detail=False, methods=['delete'])
    def clean(self, request):
        OperLog.objects.all().delete()
        return self.ok('操作日志已清空')


class LogininforViewSet(BaseViewSet, ExportExcelMixin):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Logininfor.objects.all()
    serializer_class = LogininforSerializer
    export_field_label = OrderedDict([
        ('info_id', '访问编号'),
        ('user_name', '用户名称'),
        ('ipaddr', '登录地址'),
        ('login_location', '登录地点'),
        ('browser', '浏览器'),
        ('os', '操作系统'),
        ('status', '登录状态'),
        ('msg', '操作信息'),
        ('login_time', '登录时间')
    ])
    export_filename = '登录日志'

    def get_queryset(self):
        queryset = super().get_queryset()
        s = LogininforQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        if data.get('ipaddr'):
            queryset = queryset.filter(ipaddr__icontains=data['ipaddr'])
        if data.get('userName'):
            queryset = queryset.filter(user_name__icontains=data['userName'])
        if data.get('status'):
            queryset = queryset.filter(status=data['status'])
        if data.get('beginTime'):
            queryset = queryset.filter(login_time__gte=data['beginTime'])
        if data.get('endTime'):
            queryset = queryset.filter(login_time__lte=data['endTime'])

        return queryset.order_by('-login_time')

    @action(detail=False, methods=['delete'])
    def clean(self, request):
        Logininfor.objects.all().delete()
        return self.ok('登录日志已清空')
