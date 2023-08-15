from django.conf.urls import url
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from myapps.tora_monitor import views as mviews




router = DefaultRouter()
router.register(prefix="monitor-jobs", viewset=mviews.MonitorJobViewSet)
router.register(prefix="disk-monitors", viewset=mviews.DiskMonitorDataViewSet)
router.register(prefix="mem-monitors", viewset=mviews.MemMonitorDataViewSet)
router.register(prefix="node-trade-monitors", viewset=mviews.NodeTradeInfoViewSet)
router.register(prefix="sms-control", viewset=mviews.SmsControlDataViewSet)
router.register(prefix="sms-records", viewset=mviews.SmsRecordDataViewSet)
router.register(prefix="toradb-monitor-cfg", viewset=mviews.ToraDatabaseMonitorCfgViewSet)
router.register(prefix="ipmi-infos",viewset=mviews.ipmiInfoDataViewSet)
router.register(prefix="fpga-monitors",viewset=mviews.FpgaMonitorDataViewSet)

urlpatterns = [
    path("", include(router.urls))
]