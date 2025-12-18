from rest_framework import serializers
from .models import User, Dept, Role, UserRole, Menu, DictType, DictData, Config, Post, UserPost, RoleMenu, Notice
from .common import snake_to_camel

class CamelCaseModelSerializer(serializers.ModelSerializer):
    camelize = True
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not getattr(self, 'camelize', True):
            return data
        return { snake_to_camel(k): v for k, v in data.items() }

class PaginationQuerySerializer(serializers.Serializer):
    pageNum = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=10)

class BaseModelSerializer(serializers.ModelSerializer):
    """
    抽取各模型通用的审计/状态字段，统一命名为驼峰，以减少重复定义。
    字段在模型中不存在时，序列化为 None；写入时不强制要求。
    """
    createBy = serializers.CharField(source='create_by', required=False, read_only=True)
    updateBy = serializers.CharField(source='update_by', required=False, read_only=True)
    createTime = serializers.DateTimeField(source='create_time', read_only=True, format='%Y-%m-%d %H:%M:%S')
    updateTime = serializers.DateTimeField(source='update_time', read_only=True, format='%Y-%m-%d %H:%M:%S')
    remark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.CharField(required=False)

    # 自动将公共字段并入子类 Meta.fields，避免每个子类重复声明
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        meta = getattr(cls, 'Meta', None)
        if not meta:
            return
        fields = getattr(meta, 'fields', None)
        default_public_fields = ['createBy', 'updateBy', 'createTime', 'updateTime', 'remark', 'status']
        if isinstance(fields, (list, tuple)):
            merged = list(fields)
            for f in default_public_fields:
                if f not in merged:
                    merged.append(f)
            meta.fields = merged


# User related
class UserSerializer(BaseModelSerializer):
    userId = serializers.IntegerField(source='id', required=False, read_only=True)
    userName = serializers.CharField(source='username', required=False)
    nickName = serializers.CharField(source='nick_name', required=False)
    dept = serializers.SerializerMethodField()
    deptId = serializers.IntegerField(source='dept_id', required=False, allow_null=True)
    roleIds = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    postIds = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    password = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = User
        fields = ['userId', 'userName', 'nickName', 'phonenumber', 'email', 'sex', 'avatar', 'status','remark','dept','deptId', 'roleIds', 'postIds', 'password']
    
    def get_dept(self, obj):
        if obj.dept_id:
            try:
                dept = Dept.objects.get(dept_id=obj.dept_id)
                return {
                    'deptId': dept.dept_id,
                    'deptName': dept.dept_name
                }
            except Dept.DoesNotExist:
                return None
        return None

    def create(self, validated_data):
        role_ids = validated_data.pop('roleIds', [])
        post_ids = validated_data.pop('postIds', [])
        password = validated_data.pop('password', None)
        
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
            
        if role_ids:
            roles = Role.objects.filter(role_id__in=role_ids)
            for role in roles:
                UserRole.objects.create(user=user, role=role)
        
        if post_ids:
            posts = Post.objects.filter(post_id__in=post_ids)
            for post in posts:
                UserPost.objects.create(user=user, post=post)
                
        return user

    def update(self, instance, validated_data):
        role_ids = validated_data.pop('roleIds', None)
        post_ids = validated_data.pop('postIds', None)
        password = validated_data.pop('password', None)
        
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        if role_ids is not None:
            UserRole.objects.filter(user=user).delete()
            roles = Role.objects.filter(role_id__in=role_ids)
            for role in roles:
                UserRole.objects.create(user=user, role=role)
                
        if post_ids is not None:
            UserPost.objects.filter(user=user).delete()
            posts = Post.objects.filter(post_id__in=post_ids)
            for post in posts:
                UserPost.objects.create(user=user, post=post)
        
        return user

class UserUpdateSerializer(UserSerializer):
    userId = serializers.IntegerField(source='id', required=True)

class PostQuerySerializer(PaginationQuerySerializer):
    postCode = serializers.CharField(required=False, allow_blank=True)
    postName = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])


class PostSerializer(BaseModelSerializer):
    postId = serializers.IntegerField(source='post_id', read_only=True)
    postCode = serializers.CharField(source='post_code')
    postName = serializers.CharField(source='post_name')
    postSort = serializers.IntegerField(source='post_sort')

    class Meta:
        model = Post
        fields = ['postId', 'postCode', 'postName', 'postSort']

class PostUpdateSerializer(PostSerializer):
    postId = serializers.IntegerField(source='post_id', required=True)

class UserQuerySerializer(PaginationQuerySerializer):
    userName = serializers.CharField(required=False, allow_blank=True)
    phonenumber = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])
    deptId = serializers.IntegerField(required=False)
    beginTime = serializers.DateTimeField(required=False)
    endTime = serializers.DateTimeField(required=False)

class UserProfileSerializer(BaseModelSerializer):
    userId = serializers.IntegerField(source='id', read_only=True)
    userName = serializers.CharField(source='username', read_only=True)
    nickName = serializers.CharField(source='nick_name')
    phonenumber = serializers.CharField()
    email = serializers.CharField()
    sex = serializers.CharField()
    avatar = serializers.CharField(read_only=True)
    dept = serializers.SerializerMethodField()
    roleIds = serializers.SerializerMethodField()
    postIds = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['userId', 'userName', 'nickName', 'phonenumber', 'email', 'sex', 'avatar', 
                 'dept_id', 'dept', 'roleIds', 'postIds', 'createTime']
    
    def get_dept(self, obj):
        if obj.dept_id:
            try:
                dept = Dept.objects.get(dept_id=obj.dept_id)
                return {
                    'deptId': dept.dept_id,
                    'deptName': dept.dept_name
                }
            except Dept.DoesNotExist:
                return None
        return None
    
    def get_roleIds(self, obj):
        return list(UserRole.objects.filter(user=obj).values_list('role_id', flat=True))
    
    def get_postIds(self, obj):
        return list(UserPost.objects.filter(user=obj).values_list('post_id', flat=True))

class UserInfoSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    userName = serializers.CharField()
    nickName = serializers.CharField()
    avatar = serializers.CharField()
    phonenumber = serializers.CharField()
    email = serializers.CharField()
    sex = serializers.CharField()
    dept = serializers.SerializerMethodField()

    def get_dept(self, obj):
        if obj.dept_id:
            try:
                dept = Dept.objects.get(dept_id=obj.dept_id)
                return {
                    'deptId': dept.dept_id,
                    'deptName': dept.dept_name
                }
            except Dept.DoesNotExist:
                return None
        return None


class ResetPwdSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    password = serializers.CharField(min_length=6, max_length=128)

class ChangeStatusSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['0','1'])

class UpdatePwdSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(min_length=6, max_length=128)
    newPassword = serializers.CharField(min_length=6, max_length=128)

class AvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField()

class AuthRoleAssignSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    roleIds = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

class AuthRoleQuerySerializer(PaginationQuerySerializer):
    userId = serializers.IntegerField()


# Dept related
class DeptSerializer(BaseModelSerializer):
    deptId = serializers.IntegerField(source='dept_id', read_only=True)
    parentId = serializers.IntegerField(source='parent_id', default=0)
    deptName = serializers.CharField(source='dept_name')
    orderNum = serializers.IntegerField(source='order_num', default=0)
    leader = serializers.CharField(required=False, allow_blank=True, default='')
    phone = serializers.CharField(required=False, allow_blank=True, default='')
    email = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = Dept
        fields = ['deptId', 'parentId', 'deptName', 'orderNum', 'leader', 'phone', 'email', 'status', 'remark']

class DeptUpdateSerializer(DeptSerializer):
    deptId = serializers.IntegerField(source='dept_id', required=True)

class DeptQuerySerializer(PaginationQuerySerializer):
    deptName = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])


# Role related
class RoleSerializer(BaseModelSerializer):
    roleId = serializers.IntegerField(source='role_id', read_only=True)
    roleName = serializers.CharField(source='role_name')
    roleKey = serializers.CharField(source='role_key')
    roleSort = serializers.IntegerField(source='role_sort', default=0)
    dataScope = serializers.CharField(source='data_scope', required=False, default='1')
    menuCheckStrictly = serializers.BooleanField(source='menu_check_strictly', default=True)
    deptCheckStrictly = serializers.BooleanField(source='dept_check_strictly', default=True)
    menuIds = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    deptIds = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)

    class Meta:
        model = Role
        fields = ['roleId', 'roleName', 'roleKey', 'roleSort', 'dataScope', 'menuCheckStrictly', 'deptCheckStrictly', 'menuIds', 'deptIds']

    def create(self, validated_data):
        menu_ids = validated_data.pop('menuIds', [])
        dept_ids = validated_data.pop('deptIds', [])
        
        role = super().create(validated_data)
        
        if menu_ids:
            RoleMenu.objects.bulk_create([RoleMenu(role=role, menu_id=mid) for mid in menu_ids])
            
        return role

    def update(self, instance, validated_data):
        menu_ids = validated_data.pop('menuIds', None)
        dept_ids = validated_data.pop('deptIds', None)
        
        role = super().update(instance, validated_data)
        
        if menu_ids is not None:
            RoleMenu.objects.filter(role=role).delete()
            RoleMenu.objects.bulk_create([RoleMenu(role=role, menu_id=mid) for mid in menu_ids])
            
        return role

class RoleUpdateSerializer(RoleSerializer):
    roleId = serializers.IntegerField(source='role_id', required=True)

class RoleQuerySerializer(PaginationQuerySerializer):
    roleName = serializers.CharField(required=False, allow_blank=True)
    roleKey = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])
    beginTime = serializers.DateTimeField(required=False)
    endTime = serializers.DateTimeField(required=False)

class RoleChangeStatusSerializer(serializers.Serializer):
    roleId = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['0','1'])

class RoleDataScopeSerializer(serializers.Serializer):
    roleId = serializers.IntegerField()
    dataScope = serializers.ChoiceField(choices=['1','2','3','4','5'])
    deptIds = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
    deptCheckStrictly = serializers.BooleanField(required=False, default=True)

# Menu related
class MenuQuerySerializer(PaginationQuerySerializer):
    menuName = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])

class MenuSerializer(BaseModelSerializer):
    menuId = serializers.IntegerField(source='menu_id', read_only=True)
    parentId = serializers.IntegerField(source='parent_id', default=0)
    menuName = serializers.CharField(source='menu_name')
    orderNum = serializers.IntegerField(source='order_num', default=0)
    path = serializers.CharField(required=False, allow_blank=True, default='')
    component = serializers.CharField(required=False, allow_blank=True, default='')
    routeName = serializers.CharField(source='route_name', required=False, allow_blank=True, default='')
    query = serializers.CharField(required=False, allow_blank=True, default='')
    isFrame = serializers.CharField(source='is_frame', default='1')
    isCache = serializers.CharField(source='is_cache', default='0')
    menuType = serializers.CharField(source='menu_type', default='M')
    visible = serializers.CharField(default='0')
    perms = serializers.CharField(required=False, allow_blank=True, default='')
    icon = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = Menu
        fields = ['menuId', 'parentId', 'menuName', 'orderNum', 'path', 'component', 'routeName', 'query', 'isFrame',
                  'isCache', 'menuType', 'visible', 'perms', 'icon']

class MenuUpdateSerializer(MenuSerializer):
    menuId = serializers.IntegerField(source='menu_id', required=True)

# DictType related
class DictTypeQuerySerializer(PaginationQuerySerializer):
    dictName = serializers.CharField(required=False, allow_blank=True)
    dictType = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])

class DictTypeSerializer(BaseModelSerializer):
    dictId = serializers.IntegerField(source='dict_id', read_only=True)
    dictName = serializers.CharField(source='dict_name')
    dictType = serializers.CharField(source='dict_type')

    class Meta:
        model = DictType
        fields = ['dictId', 'dictName', 'dictType']

class DictTypeUpdateSerializer(DictTypeSerializer):
    dictId = serializers.IntegerField(source='dict_id', required=True)

# DictData related
class DictDataQuerySerializer(PaginationQuerySerializer):
    dictLabel = serializers.CharField(required=False, allow_blank=True)
    dictType = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0','1'])

class DictDataSerializer(BaseModelSerializer):
    dictCode = serializers.IntegerField(source='dict_code', read_only=True)
    dictSort = serializers.IntegerField(source='dict_sort', default=0)
    dictLabel = serializers.CharField(source='dict_label')
    dictValue = serializers.CharField(source='dict_value')
    dictType = serializers.CharField(source='dict_type')
    cssClass = serializers.CharField(source='css_class', allow_blank=True, required=False, default='')
    listClass = serializers.CharField(source='list_class', allow_blank=True, required=False, default='')

    class Meta:
        model = DictData
        fields = ['dictCode', 'dictSort', 'dictLabel', 'dictValue', 'dictType', 'cssClass', 'listClass']

class DictDataUpdateSerializer(DictDataSerializer):
    dictCode = serializers.IntegerField(source='dict_code', required=True)

# Config related
class ConfigQuerySerializer(PaginationQuerySerializer):
    configName = serializers.CharField(required=False, allow_blank=True)
    configKey = serializers.CharField(required=False, allow_blank=True)
    configType = serializers.ChoiceField(required=False, choices=['Y','N'])
    beginTime = serializers.DateTimeField(required=False)
    endTime = serializers.DateTimeField(required=False)

class ConfigSerializer(BaseModelSerializer):
    configId = serializers.IntegerField(source='config_id', read_only=True)
    configName = serializers.CharField(source='config_name')
    configKey = serializers.CharField(source='config_key')
    configValue = serializers.CharField(source='config_value')
    configType = serializers.CharField(source='config_type', default='Y')

    class Meta:
        model = Config
        fields = ['configId', 'configName', 'configKey', 'configValue', 'configType']

class ConfigUpdateSerializer(ConfigSerializer):
    configId = serializers.IntegerField(source='config_id', required=True)

# Notice related
class NoticeQuerySerializer(PaginationQuerySerializer):
    noticeTitle = serializers.CharField(required=False, allow_blank=True)
    createBy = serializers.CharField(required=False, allow_blank=True)
    noticeType = serializers.CharField(required=False, allow_blank=True)

class NoticeSerializer(BaseModelSerializer):
    noticeId = serializers.IntegerField(source='notice_id', read_only=True)
    noticeTitle = serializers.CharField(source='notice_title')
    noticeType = serializers.CharField(source='notice_type')
    noticeContent = serializers.CharField(source='notice_content', allow_blank=True, required=False)
    
    class Meta:
        model = Notice
        fields = ['noticeId', 'noticeTitle', 'noticeType', 'noticeContent', 'status', 'remark', 'createBy', 'createTime']

class NoticeUpdateSerializer(NoticeSerializer):
    noticeId = serializers.IntegerField(source='notice_id', required=True)
