"""
URL configuration for ruoyi-django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # path('admin/', admin.site.urls),
    # 1. 前端入口页面：访问根路径时返回 Vue 的 index.html
    path('/', TemplateView.as_view(template_name='index.html')),
    # # 2. 处理 Vue 路由的 History 模式（可选，若 Vue 用了 History 模式）
    re_path(r'^/.*$', TemplateView.as_view(template_name='index.html')),
    path('api/', include('apps.system.urls')),
    path('api/captcha/', include('captcha.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

]
