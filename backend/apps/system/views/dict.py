from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache

from ..models import DictType, DictData
from ..serializers import (
    DictTypeSerializer, DictDataSerializer,
    DictTypeQuerySerializer, DictDataQuerySerializer
)
from ..permission import HasRolePermission
from .core import BaseViewSet


class DictTypeViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = DictType.objects.filter(del_flag='0').order_by('-create_time')
    serializer_class = DictTypeSerializer
    update_body_serializer_class = DictTypeSerializer
    update_body_id_field = 'dict_id'

    def get_queryset(self):
        qs = DictType.objects.filter(del_flag='0')
        s = DictTypeQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        dict_name = data.get('dictName', '')
        dict_type = data.get('dictType', '')
        status_value = data.get('status', '')
        if dict_name:
            qs = qs.filter(dict_name__icontains=dict_name)
        if dict_type:
            qs = qs.filter(dict_type__icontains=dict_type)
        if status_value:
            qs = qs.filter(status=status_value)
        return qs.order_by('-create_time')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # 更新该类型缓存
        dict_type = serializer.instance.dict_type
        cache_key = f'dict_data_by_type:{dict_type}'
        qs = DictData.objects.filter(dict_type=dict_type, status='0', del_flag='0').order_by('dict_sort', 'dict_label')
        data = self.get_serializer(qs, many=True).data
        cache.set(cache_key, data, timeout=3600)
        return Response({'code': 200, 'msg': '操作成功'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_type = instance.dict_type
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # 如果类型发生变化，同时更新旧类型与新类型缓存
        new_type = serializer.instance.dict_type
        for t in {old_type, new_type}:
            cache_key = f'dict_data_by_type:{t}'
            qs = DictData.objects.filter(dict_type=t, status='0', del_flag='0').order_by('dict_sort', 'dict_label')
            data = DictDataSerializer(qs, many=True).data
            cache.set(cache_key, data, timeout=3600)
        return Response({'code': 200, 'msg': '操作成功'})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.del_flag = '1'
        instance.save(update_fields=['del_flag'])
        # 刷新对应类型缓存
        dict_type = instance.dict_type
        cache_key = f'dict_data_by_type:{dict_type}'
        qs = DictData.objects.filter(dict_type=dict_type, status='0', del_flag='0').order_by('dict_sort', 'dict_label')
        data = self.get_serializer(qs, many=True).data
        cache.set(cache_key, data, timeout=3600)
        return Response({'code': 200, 'msg': '操作成功'})

    @action(detail=False, methods=['delete'], url_path='refreshCache')
    def refreshCache(self, request):
        cache.delete('dict_optionselect')
        return Response({'code': 200, 'msg': '操作成功'})

    @action(detail=False, methods=['get'], url_path='optionselect')
    def optionselect(self, request):
        cached = cache.get('dict_optionselect')
        if cached is not None:
            return Response({'code': 200, 'msg': '操作成功', 'data': cached})
        qs = DictType.objects.filter(status='0', del_flag='0').order_by('dict_name')
        data = [{'dictId': d.dict_id, 'dictName': d.dict_name, 'dictType': d.dict_type} for d in qs]
        cache.set('dict_optionselect', data, timeout=300)
        return Response({'code': 200, 'msg': '操作成功', 'data': data})


class DictDataViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = DictData.objects.filter(del_flag='0').order_by('-create_time')
    serializer_class = DictDataSerializer
    update_body_serializer_class = DictDataSerializer
    update_body_id_field = 'dict_code'

    def get_queryset(self):
        qs = DictData.objects.filter(del_flag='0')
        s = DictDataQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        dict_type = data.get('dictType', '')
        dict_label = data.get('dictLabel', '')
        status_value = data.get('status', '')
        if dict_type:
            qs = qs.filter(dict_type=dict_type)
        if dict_label:
            qs = qs.filter(dict_label__icontains=dict_label)
        if status_value:
            qs = qs.filter(status=status_value)
        return qs.order_by('-create_time')

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response({'code': 200, 'msg': '操作成功', 'rows': serializer.data, 'total': len(serializer.data)})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        return Response({'code': 200, 'msg': '操作成功', 'data': data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'code': 200, 'msg': '操作成功'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'code': 200, 'msg': '操作成功'})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.del_flag = '1'
        instance.save(update_fields=['del_flag'])
        return Response({'code': 200, 'msg': '操作成功'})

    @action(detail=False, methods=['get'], url_path='list')
    def list_action(self, request):
        # 兼容前端 /system/dict/data/list
        return self.list(request)

    @action(detail=False, methods=['get'], url_path=r'type/(?P<dict_type>[^/]+)')
    def by_type(self, request, dict_type=None):
        cache_key = f'dict_data_by_type:{dict_type}'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response({'code': 200, 'msg': '操作成功', 'data': cached})
        qs = DictData.objects.filter(dict_type=dict_type, status='0', del_flag='0').order_by('dict_sort', 'dict_label')
        serializer = self.get_serializer(qs, many=True)
        cache.set(cache_key, serializer.data, timeout=3600)
        return Response({'code': 200, 'msg': '操作成功', 'data': serializer.data})