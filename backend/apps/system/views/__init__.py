from .core import (
    CaptchaView, LoginView, GetInfoView, LogoutView, GetRoutersView
)
from .user import UserViewSet
from .menu import MenuViewSet
from .role import RoleViewSet
from .dept import DeptViewSet
from .dict import DictTypeViewSet, DictDataViewSet
from .config import ConfigViewSet
__all__ = [
    'CaptchaView', 'LoginView', 'GetInfoView', 'LogoutView', 'GetRoutersView',
    'DictTypeViewSet', 'DictDataViewSet', 'ConfigViewSet',
    'UserViewSet', 'MenuViewSet', 'RoleViewSet', 'DeptViewSet'
]