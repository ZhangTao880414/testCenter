from django.conf.urls import url
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from toraapp import views
#from toraapp.api import user_api

router = DefaultRouter()
router.register(prefix="server-users", viewset=views.SystemUserInfoViewSet)
router.register(prefix="vpn-users", viewset=views.VpnUserInfoViewSet)
router.register(prefix="vpn-cfgs", viewset=views.VpnCfgInfoViewSet)
router.register(prefix="node-infos", viewset=views.NodeInfoViewSet)
router.register(prefix="trade-nodes", viewset=views.TradeNodeViewSet)
router.register(prefix="tora-mqs", viewset=views.ToraMqViewSet)
router.register(prefix="tora-mqgroups", viewset=views.ToraMqGroupViewSet)
router.register(prefix="share-servers", viewset=views.ShareServerInfoViewSet)
#router.register(prefix="user-profiles", viewset=views.UserProfileViewSet)
router.register(prefix="node-details", viewset=views.NodeDetailInfoViewSet)
router.register(prefix="area-infos", viewset=views.AreaViewSet)
router.register(prefix="globle-paras", viewset=views.GlobleParaViewSet)
router.register(prefix="access-applys", viewset=views.AccessApplyInfoViewSet)
#router.register(prefix="query_share_servers", viewset=views.QueryShareServerView)


urlpatterns = [
    # # 用户注册和登录
    # path('register/', user_api.RegisterApi.as_view(), ),
    # path('login/', user_api.LoginAPI.as_view(), ),
    # path('logout/', user_api.UserLogout.as_view(), ),
    # path('user/info/<key>', user_api.GetUserInfo.as_view(), ),
    # path('userDel/<pk>', user_api.UserDel.as_view(), ),
    # path('userUpdate/<pk>', user_api.UserUpdate.as_view(), ),
    # path('userTest/<pk>', user_api.UserTest.as_view(), ),
    # url(r'^server-users/$', views.SystemUserInfoList.as_view()),
    # url(r'^server-users/(?P<pk>[0-9]+)/$', views.SystemUserInfoDetail.as_view()),
    url(r'^logout/', views.LogoutView.as_view(), ),
    url(r'^tora-customers/$', views.ToraCustomerList.as_view()),
    url(r'^tora-customers/(?P<pk>[0-9]+)/$', views.ToraCustomerDetail.as_view()),
    url(r'^shelf-machines/$', views.ShelfMachineList.as_view()),
    url(r'^shelf-machines/(?P<pk>[0-9]+)/$', views.ShelfMachineDetail.as_view()),
    url(r'^tora-services/$', views.ToraServiceList.as_view()),
    url(r'^tora-services/(?P<pk>[0-9]+)/$', views.ToraServiceDetail.as_view()),
    url(r'^task-flows/$', views.TaskFlowList.as_view()),
    url(r'^task-flows/(?P<pk>[0-9]+)/$', views.TaskFlowDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^choices-data/$', views.ChoicesView.as_view()),
    url(r'^tora-fronts/$', views.ToraFrontAddrView.as_view()),
    url(r'^query_share_servers/$', views.QueryShareServerView.as_view()),
    url(r'^is_vpn_exsit/$', views.IsVpnExsitView.as_view()),
    url(r'^upgrade-tasks/$', views.UpgradeTaskViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^upgrade-tasks/(?P<pk>[0-9]+)/$', views.UpgradeTaskViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
        })),
    url(r'^user-profiles/$', views.UserProfileViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^user-profiles/(?P<pk>[0-9]+)/$', views.UserProfileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
        })),
    path("", include(router.urls))
]

#urlpatterns = format_suffix_patterns(urlpatterns)

# snippet_list = SnippetViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
# snippet_detail = SnippetViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })