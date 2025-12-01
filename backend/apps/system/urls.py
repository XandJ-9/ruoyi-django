from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, MenuViewSet, RoleViewSet, DeptViewSet, LoginView, CaptchaView, GetInfoView, LogoutView, GetRoutersView,
    DictTypeViewSet, DictDataViewSet, ConfigViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r'user', UserViewSet, basename='user')
router.register(r'menu', MenuViewSet, basename='menu')
router.register(r'role', RoleViewSet, basename='role')
router.register(r'dept', DeptViewSet, basename='dept')
router.register(r'dict/type', DictTypeViewSet, basename='dict-type')
router.register(r'dict/data', DictDataViewSet, basename='dict-data')
router.register(r'config', ConfigViewSet, basename='config')

urlpatterns = [
    # 兼容前端集合 PUT 路由，需在 include(router.urls) 之前以确保优先匹配
    # 同时兼容前端 POST 路由创建新资源
    path('menu', MenuViewSet.as_view({'put': 'update_by_body','post': 'create'}), name='menu-update-body'),
    path('user', UserViewSet.as_view({'put': 'update_by_body','post': 'create'}), name='user-update-body'),
    path('role', RoleViewSet.as_view({'put': 'update_by_body','post': 'create'}), name='role-update-body'),
    path('dept', DeptViewSet.as_view({'put': 'update_by_body','post': 'create'}), name='dept-update-body'),
    path('config', ConfigViewSet.as_view({'put': 'update_by_body'}), name='config-update-body'),
    path('dict/type', DictTypeViewSet.as_view({'put': 'update_by_body'}), name='dict-type-update-body'),
    path('dict/data', DictDataViewSet.as_view({'put': 'update_by_body'}), name='dict-data-update-body'),

    # 其余 REST 路由
    path('', include(router.urls)),
]