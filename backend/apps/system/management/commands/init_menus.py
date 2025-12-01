from django.core.management.base import BaseCommand
from django.utils import timezone

from system.models import Menu


class Command(BaseCommand):
    help = "Initialize base menus: 系统管理/用户管理/部门管理/菜单管理/字典管理/系统配置管理"

    def handle(self, *args, **options):
        now = timezone.now()

        # 根目录：系统管理
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
        root, created_root = Menu.objects.get_or_create(
            parent_id=0, path='/system', menu_type='M', defaults=root_defaults
        )
        if not created_root:
            # 确保可见与启用
            for k, v in root_defaults.items():
                setattr(root, k, getattr(root, k) or v)
            root.visible = '0'
            root.status = '0'
            root.del_flag = '0'
            root.update_time = now
            root.save()

        # 子菜单：用户管理
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
        user_menu, created_user = Menu.objects.get_or_create(
            parent_id=root.menu_id, path='user', menu_type='C', defaults=user_defaults
        )
        if not created_user:
            for k, v in user_defaults.items():
                setattr(user_menu, k, getattr(user_menu, k) or v)
            user_menu.visible = '0'
            user_menu.status = '0'
            user_menu.del_flag = '0'
            user_menu.update_time = now
            user_menu.save()

        # 子菜单：部门管理
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
        dept_menu, created_dept = Menu.objects.get_or_create(
            parent_id=root.menu_id, path='dept', menu_type='C', defaults=dept_defaults
        )
        if not created_dept:
            for k, v in dept_defaults.items():
                setattr(dept_menu, k, getattr(dept_menu, k) or v)
            dept_menu.visible = '0'
            dept_menu.status = '0'
            dept_menu.del_flag = '0'
            dept_menu.update_time = now
            dept_menu.save()

        # 子菜单：菜单管理
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
        menu_menu, created_menu = Menu.objects.get_or_create(
            parent_id=root.menu_id, path='menu', menu_type='C', defaults=menu_defaults
        )
        if not created_menu:
            for k, v in menu_defaults.items():
                setattr(menu_menu, k, getattr(menu_menu, k) or v)
            menu_menu.visible = '0'
            menu_menu.status = '0'
            menu_menu.del_flag = '0'
            menu_menu.update_time = now
            menu_menu.save()

        # 子菜单：字典管理
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
        dict_menu, created_dict = Menu.objects.get_or_create(
            parent_id=root.menu_id, path='dict', menu_type='C', defaults=dict_defaults
        )
        if not created_dict:
            for k, v in dict_defaults.items():
                setattr(dict_menu, k, getattr(dict_menu, k) or v)
            dict_menu.visible = '0'
            dict_menu.status = '0'
            dict_menu.del_flag = '0'
            dict_menu.update_time = now
            dict_menu.save()

        # 子菜单：系统配置管理
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
        config_menu, created_config = Menu.objects.get_or_create(
            parent_id=root.menu_id, path='config', menu_type='C', defaults=config_defaults
        )
        if not created_config:
            for k, v in config_defaults.items():
                setattr(config_menu, k, getattr(config_menu, k) or v)
            config_menu.visible = '0'
            config_menu.status = '0'
            config_menu.del_flag = '0'
            config_menu.update_time = now
            config_menu.save()

        self.stdout.write(self.style.SUCCESS('Initialized menus: 系统管理/用户管理/部门管理/菜单管理/字典管理/系统配置管理'))