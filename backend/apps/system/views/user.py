from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from .core import BaseViewSet
from ..permission import HasRolePermission
from ..common import audit_log
from apps.common.mixins import ExportExcelMixin
from collections import OrderedDict
from ..serializers import (
    UserSerializer, DeptSerializer, UserProfileSerializer, RoleSerializer, PostSerializer,
    UserQuerySerializer, ResetPwdSerializer, ChangeStatusSerializer,
    UpdatePwdSerializer, AvatarSerializer, AuthRoleAssignSerializer, AuthRoleQuerySerializer,
    UserUpdateSerializer
)
from ..models import User, Dept, Role, UserRole, Post, UserPost

from drf_spectacular.utils import extend_schema

class UserViewSet(BaseViewSet, ExportExcelMixin):
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    update_body_serializer_class = UserUpdateSerializer
    export_field_label = OrderedDict([
        ('id', '用户序号'),
        ('username', '登录名称'),
        ('nick_name', '用户昵称'),
        ('email', '用户邮箱'),
        ('phonenumber', '手机号码'),
        ('sex', '用户性别'),
        ('status', '帐号状态'),
        ('login_ip', '最后登录IP'),
        ('login_date', '最后登录时间'),
        ('dept.dept_name', '部门名称'),
        ('create_by', '创建者'),
        ('create_time', '创建时间'),
        ('remark', '备注')
    ])
    export_filename = '用户数据'
    def get_queryset(self):
        queryset = super().get_queryset()
        s = UserQuerySerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        user_name = data.get('userName') or ''
        phonenumber = data.get('phonenumber') or ''
        status_value = data.get('status') or ''
        dept_id = data.get('deptId')
        begin_time = data.get('beginTime')
        end_time = data.get('endTime')
        if user_name:
            queryset = queryset.filter(Q(username__icontains=user_name) | Q(nick_name__icontains=user_name))
        if phonenumber:
            queryset = queryset.filter(phonenumber__icontains=phonenumber)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if dept_id:
            queryset = queryset.filter(dept_id=dept_id)
        if begin_time:
            queryset = queryset.filter(create_time__gte=begin_time)
        if end_time:
            queryset = queryset.filter(create_time__lte=end_time)
        return queryset.order_by('-create_time')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        roles = Role.objects.filter(status='0', del_flag='0')
        posts = Post.objects.filter(status='0', del_flag='0')
        
        # 获取用户关联的角色ID和岗位ID
        role_ids = list(UserRole.objects.filter(user=instance).values_list('role_id', flat=True))
        post_ids = list(UserPost.objects.filter(user=instance).values_list('post_id', flat=True))
        
        data = serializer.data
        return self.raw_response({
            'data': data,
            'roles': RoleSerializer(roles, many=True).data,
            'posts': PostSerializer(posts, many=True).data,
            'roleIds': role_ids,
            'postIds': post_ids
        })

    @action(detail=False, methods=['put'])
    @audit_log
    def resetPwd(self, request):
        v = ResetPwdSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        user_id = v.validated_data['userId']
        password = v.validated_data['password']
        try:
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            return self.ok('密码重置成功')
        except User.DoesNotExist:
            return self.not_found('用户不存在')
    
    @action(detail=False, methods=['put'])
    @audit_log
    def changeStatus(self, request):
        v = ChangeStatusSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        user_id = v.validated_data['userId']
        status_value = v.validated_data['status']
        try:
            user = User.objects.get(id=user_id)
            user.status = status_value
            user.save()
            return self.ok('状态修改成功')
        except User.DoesNotExist:
            return self.not_found('用户不存在')
    
    @action(detail=False, methods=['get'])
    def deptTree(self, request):
        # 仅返回启用状态的部门，按父子关系与排序号组织
        depts = Dept.objects.filter(status='0').order_by('parent_id', 'order_num')
        serializer = DeptSerializer(depts, many=True)

        # 将序列化数据转换为前端期望的树形结构：id/label/children
        raw_items = serializer.data
        mapped = [
            {
                'id': item['deptId'],
                'label': item['deptName'],
                'parentId': item['parentId'],
                # 为兼容筛选逻辑保留 disabled 字段（当前均为启用）
                'disabled': False,
            }
            for item in raw_items
        ]

        def build_tree(nodes, parent_id=0):
            tree = []
            for n in nodes:
                if n['parentId'] == parent_id:
                    children = build_tree(nodes, n['id'])
                    node = {
                        'id': n['id'],
                        'label': n['label'],
                    }
                    if children:
                        node['children'] = children
                    # 仅当为禁用时传递该标记；保持输出简洁
                    if n.get('disabled'):
                        node['disabled'] = True
                    tree.append(node)
            return tree

        tree_data = build_tree(mapped)
        return self.data(tree_data)
    
    @action(detail=False, methods=['get'], url_path=r'profile')
    def profile(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        # 获取用户所属的角色组和岗位组名称
        role_names = list(UserRole.objects.filter(user=user).values_list('role__role_name', flat=True))
        post_names = list(UserPost.objects.filter(user=user).values_list('post__post_name', flat=True))
        
        data = {
            'data': serializer.data,
            'roleGroup': ','.join(role_names),
            'postGroup': ','.join(post_names)
        }
        return self.raw_response(data)

    @action(detail=False, methods=['put'], url_path=r'updateProfile')
    @audit_log
    def updateProfile(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.ok('个人信息修改成功')
    
    @action(detail=False, methods=['put'], url_path=r'profile/updatePwd')
    @audit_log
    def updatePwd(self, request):
        v = UpdatePwdSerializer(data=request.data)
        v.is_valid(raise_exception=True)
        old_password = v.validated_data['oldPassword']
        new_password = v.validated_data['newPassword']
        user = request.user
        if not user.check_password(old_password):
            return self.error('旧密码错误')
        
        user.set_password(new_password)
        user.save()
        return self.ok('密码修改成功')
    
    @action(detail=False, methods=['post'], url_path=r'profile/avatar')
    @audit_log
    def avatar(self, request):
        avatar_file = request.FILES.get('avatarfile')
        if not avatar_file:
            return self.error('未上传文件')
            
        # 保存文件到本地 (实际生产环境建议对接云存储)
        import os
        from django.conf import settings
        import uuid
        
        # 确保目录存在
        upload_dir = os.path.join(settings.BASE_DIR, 'media', 'avatar')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成文件名
        ext = os.path.splitext(avatar_file.name)[1]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, 'wb+') as destination:
            for chunk in avatar_file.chunks():
                destination.write(chunk)
                
        # 构建访问URL
        avatar_url = f"/media/avatar/{filename}"
        
        user = request.user
        user.avatar = avatar_url
        user.save()
        
        return self.raw_response({'code': 200, 'msg': '头像上传成功', 'imgUrl': avatar_url})
    
    @action(detail=False, methods=['get'], url_path=r'authRole/(?P<userId>[^/]+)')
    def getAuthRole(self, request, userId = None):
        v = AuthRoleQuerySerializer(data={'userId': userId})
        v.is_valid(raise_exception=True)
        user_id = v.validated_data['userId']
        try:
            user = User.objects.get(id=user_id)
            roles = Role.objects.filter(status='0', del_flag='0')
            user_roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
            
            roles_data = []
            for role in roles:
                role_data = RoleSerializer(role).data
                role_data['flag'] = role.role_id in user_roles
                roles_data.append(role_data)
            
            return self.raw_response({'user': UserSerializer(user).data, 'roles': roles_data})
        except User.DoesNotExist:
            return self.not_found('用户不存在')
    
    @action(detail=False, methods=['put'], url_path=r'authRole')
    @audit_log
    @extend_schema(request=AuthRoleAssignSerializer)
    def updateAuthRole(self, request):
        v = AuthRoleAssignSerializer(data=request.query_params)
        v.is_valid(raise_exception=True)
        user_id = v.validated_data['userId']
        role_ids = v.validated_data.get('roleIds', [])
        try:
            user = User.objects.get(id=user_id)
            UserRole.objects.filter(user=user).delete()
            for role_id in role_ids:
                try:
                    role = Role.objects.get(role_id=role_id)
                    UserRole.objects.create(user=user, role=role)
                except Role.DoesNotExist:
                    continue
            return self.ok('授权成功')
        except User.DoesNotExist:
            return self.not_found('用户不存在')
