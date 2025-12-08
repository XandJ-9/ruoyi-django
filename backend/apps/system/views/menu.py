from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from .core import BaseViewSet
from ..permission import HasRolePermission
from ..models import Menu, RoleMenu
from ..serializers import MenuSerializer, MenuQuerySerializer, MenuCreateSerializer, MenuUpdateSerializer


class MenuViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Menu.objects.filter(del_flag='0').order_by('parent_id', 'order_num')
    serializer_class = MenuSerializer
    update_body_serializer_class = MenuUpdateSerializer
    update_body_id_field = 'menuId'

    def list(self, request, *args, **kwargs):
        s = MenuQuerySerializer(data=request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        menu_name = data.get('menuName')
        status_value = data.get('status')
        qs = self.get_queryset()
        if menu_name:
            qs = qs.filter(menu_name__icontains=menu_name)
        if status_value:
            qs = qs.filter(status=status_value)
        # page = self.paginate_queryset(qs)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response({"code": 200, "msg": "操作成功", "data": serializer.data})

    def create(self, request, *args, **kwargs):
        v = MenuCreateSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        serializer = self.get_serializer(data=v.validated_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.ok()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.ok()

    @action(detail=False, methods=['get'])
    def treeselect(self, request):
        qs = self.get_queryset()
        items = list(qs)

        def build_tree(items, pid=0):
            res = []
            for m in items:
                if m.parent_id == pid:
                    node = {"id": m.menu_id, "label": m.menu_name}
                    children = build_tree(items, m.menu_id)
                    if children:
                        node["children"] = children
                    res.append(node)
            return res

        data = build_tree(items, 0)
        return Response({"code": 200, "msg": "操作成功", "data": data})

    @action(detail=False, methods=['get'], url_path=r'roleMenuTreeselect/(?P<roleId>\d+)')
    def roleMenuTreeselect(self, request, roleId=None):
        qs = self.get_queryset()
        items = list(qs)
        checked = list(RoleMenu.objects.filter(role_id=roleId).values_list('menu_id', flat=True))

        def build_tree(items, pid=0):
            res = []
            for m in items:
                if m.parent_id == pid:
                    node = {"id": m.menu_id, "label": m.menu_name}
                    children = build_tree(items, m.menu_id)
                    if children:
                        node["children"] = children
                    res.append(node)
            return res

        data = build_tree(items, 0)
        return Response({"code": 200, "msg": "操作成功", "menus": data, "checkedKeys": checked})