"""ToraOps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from myapps.toraapp import views as tv
from rest_framework.authtoken import views
from myapps.tora_monitor import urls as monitor_urls
from django.views import static
from django.conf import settings 


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include('myapps.toraapp.urls')),
    url(r'^', include('myapps.tora_monitor.urls')),
    #path('monitor/', monitor_urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^api-token-auth/', tv.obtain_expiring_auth_token),
    # url(r'^users/$', tv.UserList.as_view()),
    # url(r'^users/(?P<pk>[0-9]+)/$', tv.UserDetail.as_view()),
    #url(r'^static/(?P<path>.*)$', static.serve, {'document_root': '/home/trade/tora_ops/ToraOps/static/'}, name='static'),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
]
