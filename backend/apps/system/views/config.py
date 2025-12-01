from django.utils.timezone import make_aware
from datetime import datetime

from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .core import BaseViewSet
from ..permission import HasRolePermission
from ..models import Config
from ..serializers import (
    ConfigSerializer,
    ConfigQuerySerializer,
    ConfigCreateSerializer,
    ConfigUpdateSerializer,
)


class ConfigViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Config.objects.filter(del_flag='0').order_by('-create_time')
    serializer_class = ConfigSerializer
    update_body_serializer_class = ConfigUpdateSerializer
    update_body_id_field = 'configId'

    def get_queryset(self):
        qs = Config.objects.filter(del_flag='0')
        s = ConfigQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        config_name = data.get('configName', '')
        config_key = data.get('configKey', '')
        config_type = data.get('configType', '')
        begin_time = data.get('beginTime')
        end_time = data.get('endTime')
        if config_name:
            qs = qs.filter(config_name__icontains=config_name)
        if config_key:
            qs = qs.filter(config_key__icontains=config_key)
        if config_type:
            qs = qs.filter(config_type=config_type)
        if begin_time:
            qs = qs.filter(create_time__gte=begin_time)
        if end_time:
            qs = qs.filter(create_time__lte=end_time)
        return qs.order_by('-create_time')

    @action(detail=False, methods=['get'], url_path='list')
    def list_action(self, request):
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response({"code": 200, "msg": "操作成功", "rows": serializer.data, "total": qs.count()})

    # 详情响应由 BaseViewSet.retrieve 统一封装

    def create(self, request, *args, **kwargs):
        v = ConfigCreateSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        vd = v.validated_data
        cfg = Config(
            config_name=vd.get('configName'),
            config_key=vd.get('configKey'),
            config_value=vd.get('configValue'),
            config_type=vd.get('configType', 'Y'),
            remark=vd.get('remark', '') or '',
        )
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'username', None):
            cfg.create_by = user.username
            cfg.update_by = user.username
        cfg.save()
        # 简单缓存：按键名缓存值
        try:
            cache.set(f"config:{cfg.config_key}", cfg.config_value, timeout=3600)
        except Exception:
            pass
        return self.ok()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        v = ConfigUpdateSerializer(instance=instance, data=request.data, partial=partial)
        v.is_valid(raise_exception=True)
        vd = v.validated_data
        for src, dst in [
            ('configName', 'config_name'),
            ('configKey', 'config_key'),
            ('configValue', 'config_value'),
            ('configType', 'config_type'),
            ('remark', 'remark'),
        ]:
            if src in vd:
                setattr(instance, dst, vd.get(src))
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'username', None):
            instance.update_by = user.username
        instance.save()
        try:
            cache.set(f"config:{instance.config_key}", instance.config_value, timeout=3600)
        except Exception:
            pass
        return self.ok()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.del_flag = '1'
        instance.save(update_fields=['del_flag'])
        try:
            cache.delete(f"config:{instance.config_key}")
        except Exception:
            pass
        return self.ok()

    # 集合更新由 BaseViewSet.update_by_body 统一实现

    @action(detail=False, methods=['get'], url_path=r'configKey/(?P<configKey>[^/]+)')
    def get_config_key(self, request, configKey=None):
        # 返回值放在 msg 字段以兼容前端用法
        value = None
        try:
            value = cache.get(f"config:{configKey}")
            if value is None:
                obj = Config.objects.filter(config_key=configKey, del_flag='0').first()
                value = obj.config_value if obj else ''
                cache.set(f"config:{configKey}", value, timeout=3600)
        except Exception:
            obj = Config.objects.filter(config_key=configKey, del_flag='0').first()
            value = obj.config_value if obj else ''
        return Response({"code": 200, "msg": value})

    @action(detail=False, methods=['delete'], url_path='refreshCache')
    def refresh_cache(self, request):
        try:
            cache.clear()
        except Exception:
            pass
        return Response({"code": 200, "msg": "操作成功"})