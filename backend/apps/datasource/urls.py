from django.urls import path, include
from .views import DataSourceViewSet


from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'', DataSourceViewSet, basename='data-source')

urlpatterns = [
    path('', include(router.urls)),
]
