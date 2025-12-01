from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .core import BaseViewSet
from ..permission import HasRolePermission
from ..models import Dept
from ..serializers import (
    DeptSerializer,
    DeptQuerySerializer,
    DeptCreateSerializer,
    DeptUpdateSerializer,
)


class DeptViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = Dept.objects.filter(del_flag='0').order_by('parent_id', 'order_num')
    serializer_class = DeptSerializer
    update_body_serializer_class = DeptUpdateSerializer
    update_body_id_field = 'deptId'

    def list(self, request, *args, **kwargs):
        s = DeptQuerySerializer(data=request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        qs = self.get_queryset()

        dept_name = data.get('deptName')
        status_value = data.get('status')
        if dept_name:
            qs = qs.filter(dept_name__icontains=dept_name)
        if status_value:
            qs = qs.filter(status=status_value)

        serializer = self.get_serializer(qs, many=True)
        return Response({"code": 200, "msg": "操作成功", "data": serializer.data})

    # 详情响应由 BaseViewSet.retrieve 统一封装

    def create(self, request, *args, **kwargs):
        v = DeptCreateSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        vd = v.validated_data

        dept = Dept(
            parent_id=vd.get('parentId', 0) or 0,
            dept_name=vd.get('deptName'),
            order_num=vd.get('orderNum', 0),
            leader=vd.get('leader', '') or '',
            phone=vd.get('phone', '') or '',
            email=vd.get('email', '') or '',
            status=vd.get('status', '0'),
        )
        # 审计字段
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'username', None):
            dept.create_by = user.username
            dept.update_by = user.username
        dept.save()
        return self.ok()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        v = DeptUpdateSerializer(instance=instance, data=request.data, partial=partial)
        v.is_valid(raise_exception=True)
        vd = v.validated_data

        for src, dst in [
            ('parentId', 'parent_id'),
            ('deptName', 'dept_name'),
            ('orderNum', 'order_num'),
            ('leader', 'leader'),
            ('phone', 'phone'),
            ('email', 'email'),
            ('status', 'status'),
        ]:
            if src in vd:
                setattr(instance, dst, vd.get(src))

        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'username', None):
            instance.update_by = user.username
        instance.save()
        return self.ok()

    # 软删除由 BaseViewSet.destroy 统一实现

    # 集合更新由 BaseViewSet.update_by_body 统一实现

    @action(detail=False, methods=['get'], url_path=r'list/exclude/(?P<deptId>\d+)')
    def list_exclude_child(self, request, deptId=None):
        # 返回排除指定部门及其所有子部门的列表（用于上级部门选择）
        try:
            root_id = int(deptId)
        except Exception:
            return Response({"code": 400, "msg": "参数错误"}, status=status.HTTP_400_BAD_REQUEST)

        items = list(self.get_queryset())
        # 计算需要排除的 id 集合
        exclude_ids = set()
        pid_to_children = {}
        for d in items:
            pid_to_children.setdefault(d.parent_id, []).append(d.dept_id)
        stack = [root_id]
        while stack:
            cur = stack.pop()
            if cur in exclude_ids:
                continue
            exclude_ids.add(cur)
            stack.extend(pid_to_children.get(cur, []))

        filtered = [d for d in items if d.dept_id not in exclude_ids]
        serializer = self.get_serializer(filtered, many=True)
        return Response({"code": 200, "msg": "操作成功", "data": serializer.data})