from django.conf.urls import url
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from myapps.tora_monitor import views as mviews




router = DefaultRouter()
router.register(prefix="monitor-jobs", viewset=mviews.MonitorJobViewSet)

urlpatterns = [
    path("", include(router.urls))
]