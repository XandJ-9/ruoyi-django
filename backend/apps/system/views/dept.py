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
