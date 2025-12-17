from rest_framework import routers
from apps.monitor.views import OperLogViewSet, LogininforViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'operlog', OperLogViewSet)
router.register(r'logininfor', LogininforViewSet)

urlpatterns = router.urls
