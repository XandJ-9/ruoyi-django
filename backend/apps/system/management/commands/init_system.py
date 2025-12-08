from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.system.models import Menu, Role, User, UserRole


class Command(BaseCommand):
    help = "Initialize menus, roles, users and bindings: 菜单、角色、用户、一键初始化"

    def handle(self, *args, **options):
        now = timezone.now()

        # 初始化系统管理目录
        root_defaults = {
            'menu_name': '系统管理',
            'order_num': 1,
            'component': '',
            'query': '',
            'is_frame': '1',
            'is_cache': '0',
            'menu_type': 'M',
            'visible': '0',
            'status': '0',
            'perms': '',
            'icon': 'system',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'remark': '系统管理目录',
            'del_flag': '0'
        }
        root, created_root = Menu.objects.get_or_create(parent_id=0, path='/system', menu_type='M', defaults=root_defaults)
        if not created_root:
            for k, v in root_defaults.items():
                setattr(root, k, getattr(root, k) or v)
            root.visible = '0'
            root.status = '0'
            root.del_flag = '0'
            root.update_time = now
            root.save()

        user_defaults = {
            'menu_name': '用户管理',
            'order_num': 1,
            'component': 'system/user/index',
            'query': '',
            'is_frame': '1',
            'is_cache': '0',
            'menu_type': 'C',
            'visible': '0',
            'status': '0',
            'perms': 'system:user:list',
            'icon': 'user',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'remark': '用户管理菜单',
            'del_flag': '0'
        }
        user_menu, created_user_menu = Menu.objects.get_or_create(parent_id=root.menu_id, path='user', menu_type='C', defaults=user_defaults)
        if not created_user_menu:
            for k, v in user_defaults.items():
                setattr(user_menu, k, getattr(user_menu, k) or v)
            user_menu.visible = '0'
            user_menu.status = '0'
            user_menu.del_flag = '0'
            user_menu.update_time = now
            user_menu.save()

        dept_defaults = {
            'menu_name': '部门管理',
            'order_num': 2,
            'component': 'system/dept/index',
            'query': '',
            'is_frame': '1',
            'is_cache': '0',
            'menu_type': 'C',
            'visible': '0',
            'status': '0',
            'perms': 'system:dept:list',
            'icon': 'dept',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'remark': '部门管理菜单',
            'del_flag': '0'
        }
        dept_menu, created_dept_menu = Menu.objects.get_or_create(parent_id=root.menu_id, path='dept', menu_type='C', defaults=dept_defaults)
        if not created_dept_menu:
            for k, v in dept_defaults.items():
                setattr(dept_menu, k, getattr(dept_menu, k) or v)
            dept_menu.visible = '0'
            dept_menu.status = '0'
            dept_menu.del_flag = '0'
            dept_menu.update_time = now
            dept_menu.save()

        menu_defaults = {
            'menu_name': '菜单管理',
            'order_num': 3,
            'component': 'system/menu/index',
            'query': '',
            'is_frame': '1',
            'is_cache': '0',
            'menu_type': 'C',
            'visible': '0',
            'status': '0',
            'perms': 'system:menu:list',
            'icon': 'tree',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'remark': '菜单管理菜单',
            'del_flag': '0'
        }
        menu_menu, created_menu_menu = Menu.objects.get_or_create(parent_id=root.menu_id, path='menu', menu_type='C', defaults=menu_defaults)
        if not created_menu_menu:
            for k, v in menu_defaults.items():
                setattr(menu_menu, k, getattr(menu_menu, k) or v)
            menu_menu.visible = '0'
            menu_menu.status = '0'
            menu_menu.del_flag = '0'
            menu_menu.update_time = now
            menu_menu.save()

        dict_defaults = {
            'menu_name': '字典管理',
            'order_num': 4,
            'component': 'system/dict/index',
            'query': '',
            'is_frame': '1',
            'is_cache': '0',
            'menu_type': 'C',
            'visible': '0',
            'status': '0',
            'perms': 'system:dict:list',
            'icon': 'dict',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'remark': '字典管理菜单',
            'del_flag': '0'
        }
        dict_menu, created_dict_menu = Menu.objects.get_or_create(parent_id=root.menu_id, path='dict', menu_type='C', defaults=dict_defaults)
        if not created_dict_menu:
            for k, v in dict_defaults.items():
                setattr(dict_menu, k, getattr(dict_menu, k) or v)
            dict_menu.visible = '0'
            dict_menu.status = '0'
            dict_menu.del_flag = '0'
            dict_menu.update_time = now
            dict_menu.save()

        config_defaults = {
            'menu_name': '系统配置管理',
            'order_num': 5,
            'component': 'system/config/index',
            'query': '',
            'is_frame': '1',
            'is_cache': '0',
            'menu_type': 'C',
            'visible': '0',
            'status': '0',
            'perms': 'system:config:list',
            'icon': 'config',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'remark': '系统配置管理菜单',
            'del_flag': '0'
        }
        config_menu, created_config_menu = Menu.objects.get_or_create(parent_id=root.menu_id, path='config', menu_type='C', defaults=config_defaults)
        if not created_config_menu:
            for k, v in config_defaults.items():
                setattr(config_menu, k, getattr(config_menu, k) or v)
            config_menu.visible = '0'
            config_menu.status = '0'
            config_menu.del_flag = '0'
            config_menu.update_time = now
            config_menu.save()

        # 初始化角色
        role_admin_defaults = {
            'role_name': '管理员',
            'role_key': 'admin',
            'role_sort': 1,
            'data_scope': '1',
            'menu_check_strictly': 1,
            'dept_check_strictly': 1,
            'status': '0',
            'remark': '',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'del_flag': '0',
        }
        role_admin, created_role_admin = Role.objects.get_or_create(role_key='admin', defaults=role_admin_defaults)
        if not created_role_admin:
            for k, v in role_admin_defaults.items():
                setattr(role_admin, k, getattr(role_admin, k) or v)
            role_admin.status = '0'
            role_admin.del_flag = '0'
            role_admin.update_time = now
            role_admin.save()

        role_common_defaults = {
            'role_name': '普通用户',
            'role_key': 'common',
            'role_sort': 2,
            'data_scope': '1',
            'menu_check_strictly': 1,
            'dept_check_strictly': 1,
            'status': '0',
            'remark': '',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'del_flag': '0',
        }
        role_common, created_role_common = Role.objects.get_or_create(role_key='common', defaults=role_common_defaults)
        if not created_role_common:
            for k, v in role_common_defaults.items():
                setattr(role_common, k, getattr(role_common, k) or v)
            role_common.status = '0'
            role_common.del_flag = '0'
            role_common.update_time = now
            role_common.save()

        msg = []
        msg.append('管理员角色已存在' if not created_role_admin else '管理员角色已创建')
        msg.append('普通用户角色已存在' if not created_role_common else '普通用户角色已创建')
        self.stdout.write(self.style.SUCCESS('；'.join(msg)))


        # 初始化用户
        admin_defaults = {
            'nick_name': '管理员',
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True,
            'status': '0',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'del_flag': '0',
        }
        admin_user, created_admin_user = User.objects.get_or_create(username='admin', defaults=admin_defaults)
        if not created_admin_user:
            for k, v in admin_defaults.items():
                setattr(admin_user, k, getattr(admin_user, k) if getattr(admin_user, k) is not None else v)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.status = '0'
            admin_user.del_flag = '0'
            admin_user.update_time = now
            admin_user.save()
        else:
            admin_user.set_password('admin123')
            admin_user.save()

        test_defaults = {
            'nick_name': '测试用户',
            'email': 'test@example.com',
            'is_staff': False,
            'is_superuser': False,
            'status': '0',
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'del_flag': '0',
        }
        test_user, created_test_user = User.objects.get_or_create(username='test', defaults=test_defaults)
        if not created_test_user:
            for k, v in test_defaults.items():
                setattr(test_user, k, getattr(test_user, k) if getattr(test_user, k) is not None else v)
            test_user.is_staff = False
            test_user.is_superuser = False
            test_user.status = '0'
            test_user.del_flag = '0'
            test_user.update_time = now
            test_user.save()
        else:
            test_user.set_password('test123')
            test_user.save()
        
        msg = []
        msg.append('admin 已存在' if not created_admin_user else 'admin 已创建 密码: admin123')
        msg.append('test 已存在' if not created_test_user else 'test 已创建 密码: test123')
        self.stdout.write(self.style.SUCCESS('；'.join(msg)))

        # 初始化用户角色绑定
        UserRole.objects.get_or_create(user=admin_user, role=role_admin, defaults={
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'del_flag': '0',
        })
        UserRole.objects.get_or_create(user=test_user, role=role_common, defaults={
            'create_by': 'system',
            'update_by': 'system',
            'create_time': now,
            'update_time': now,
            'del_flag': '0',
        })

        parts = []
        parts.append('菜单已初始化')
        parts.append('角色已初始化')
        parts.append('用户已初始化')
        parts.append('用户角色绑定完成')
        self.stdout.write(self.style.SUCCESS('；'.join(parts)))
