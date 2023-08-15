#from django.shortcuts import render
#from toraapp.models import server_user_info, ToraCustomer
#from toraapp.serializers import SystemUserInfo_Serializers, UserSerializer
from myapps.toraapp import models
from django.forms.models import model_to_dict
from django.db.models import Q
from rest_framework import serializers
import myapps.toraapp.serializers as tora_ser
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
#from django.views import View
import datetime
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.db.models.signals import post_init, post_save, m2m_changed
from myapps.toraapp.tools import signals
from django.dispatch import receiver
from myapps.toraapp import callback
from myapps.toraapp.filters import TaskFlowFilter
import common.tora_django_common as tdc
import json
import datetime
import logging
logger = logging.getLogger('django')

# Create your views here.


# from apscheduler.schedulers.background import BackgroundScheduler
# from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
 
# scheduler = BackgroundScheduler()
# scheduler.add_jobstore(DjangoJobStore(), "default")
 
 
# # 时间间隔3秒钟打印一次当前的时间
# @register_job(scheduler, "interval", seconds=3, id='test_job')
# def test_job():
#     print("我是apscheduler任务")
# # per-execution monitoring, call register_events on your scheduler
# register_events(scheduler)
# scheduler.start()
# print("Scheduler started!")




@receiver(post_save, sender=models.SystemUserInfo)
def do_something(sender, instance=None, created=False, **kwargs):
    if created:
        print("do something!")
        print("sender", sender, type(sender))
        print(instance)


#REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES为setting里设置的过期时间
EXPIRE_MINUTES = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES', 1)

class ObtainExpiringAuthToken(ObtainAuthToken):
    """Create user token"""
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token, created =  Token.objects.get_or_create(user=serializer.validated_data['user'])
            username = serializer.validated_data['user'].username
            user_obj = User.objects.get(username = serializer.validated_data['user'].username)
            user_data = model_to_dict(user_obj)
            del user_data['password']
            del user_data['user_permissions']
            if user_data['last_login'] != None:
                user_data['last_login'] = user_data['last_login'].strftime("%Y-%m-%d %H:%M:%S")
            else:
                user_data['last_login'] = None
            user_data['date_joined'] = user_data['date_joined'].strftime("%Y-%m-%d %H:%M:%S")
            #user_data['user_permissions'] = str(user_data['user_permissions'])

            userprofile_obj = models.UserProfile.objects.get(user=serializer.validated_data['user'])
            userprofile_data = model_to_dict(userprofile_obj)
            userprofile_data['user'] = str(userprofile_data['user'])
            userprofile_data['avatar'] = str(userprofile_data['avatar'])

            time_now = datetime.datetime.now()
 
            if created or token.created < time_now - datetime.timedelta(minutes=EXPIRE_MINUTES):
                # Update the created time of the token to keep it valid
                token.delete()
                token = Token.objects.create(user=serializer.validated_data['user'])
                token.created = time_now
                token.save()
            res = {'token': token.key, 'user': user_data, 'userprofile': userprofile_data}
            # print(type(res))    
            # j_data = json.dumps({'token': token.key, 'user': user_data, 'userprofile': userprofile_data})
            # print(j_data)
            # print("j_data:",type(j_data))
            return Response(res)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()




class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = tora_ser.UserSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('username', 'email')
    ordering_fields = ['date_joined']
    #ordering = ['-id']


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = tora_ser.UserSerializer
    permission_classes = (IsAdminUser,)


# class SystemUserInfoList(generics.ListCreateAPIView):
#     queryset = models.SystemUserInfo.objects.all()
#     serializer_class = tora_ser.SystemUserInfo_Serializers
#     permission_classes = (IsAuthenticated,)
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ('inner_ip', 'cur_status')
#     ordering_fields = ['create_time']

#     def perform_create(self, serializer):
#         serializer.save(operator=self.request.user)
#         print("request.user:",self.request.user)


# class SystemUserInfoDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = models.SystemUserInfo.objects.all()
#     serializer_class = tora_ser.SystemUserInfo_Serializers
#     permission_classes = (IsAuthenticated,)


class SystemUserInfoViewSet(viewsets.ModelViewSet):
    queryset = models.SystemUserInfo.objects.all()
    serializer_class = tora_ser.SystemUserInfo_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('inner_ip', 'sys_user_name', 'cur_status','customer')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)
        print("request.user:",self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        req_data = self.request.data
        passwd = req_data["sys_user_passwd"]
        print("passwd:", req_data["sys_user_passwd"])
        # if passwd == '1qaz@WSX':
        #     signals.post_update.send(sender=models.SystemUserInfo, sys_user_passwd=passwd)


class VpnUserInfoViewSet(viewsets.ModelViewSet):
    queryset = models.VpnUserInfo.objects.all()
    serializer_class = tora_ser.VpnUserInfo_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('engine_room', 'vpn_user_name', 'vpn_phone', 'cur_status', 'customer')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)
        #print("request.user:",self.request.user)

class VpnCfgInfoViewSet(viewsets.ModelViewSet):
    queryset = models.VpnCfgInfo.objects.all()
    serializer_class = tora_ser.VpnCfgInfo_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('engine_room', 'vpn_address')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)
        #print("request.user:",self.request.user)

    # def perform_update(self, serializer):
    #     serializer.save()
    #     req_data = self.request.data
    #     passwd = req_data["sys_user_passwd"]
    #     print("passwd:", req_data["sys_user_passwd"])


class ToraCustomerList(generics.ListCreateAPIView):
    queryset = models.ToraCustomer.objects.all()
    serializer_class = tora_ser.ToraCustomer_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('custgroup_name', 'phone')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)


class ToraCustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ToraCustomer.objects.all()
    serializer_class = tora_ser.ToraCustomer_Serializers
    permission_classes = (IsAuthenticated,)
    


class ShelfMachineList(generics.ListCreateAPIView):
    queryset = models.ShelfMachine.objects.all()
    serializer_class = tora_ser.ShelfMachine_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('engine_room', 'room_no', 'row_no', 'cabinet', 'purpose', 'assert_type', 'serial_number', 
                        'IT_checked_number', 'assert_number', 'node_id', 'inner_ip', 'high_trade_ip')
    ordering_fields = ['inner_ip']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)


class ShelfMachineDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ShelfMachine.objects.all()
    serializer_class = tora_ser.ShelfMachine_Serializers
    permission_classes = (IsAuthenticated,)


class TaskFlowList(generics.ListCreateAPIView):
    queryset = models.TaskFlow.objects.all()
    serializer_class = tora_ser.TaskFlow_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ('task_status', 'engine_room', 'serial_number', 'IT_checked_number',
    #                      'node_id', 'inner_ip', 'customer', 'create_time')
    # 指定过滤器类
    filter_class = TaskFlowFilter
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        
        print(type(self.request.data), self.request.data)
        #4服务器维修，不需要根据vpn账号增加客户处理
        if self.request.data['task_type'] not in ['4']:
            if ('customer' not in self.request.data.keys()) or self.request.data['customer'] == None:
                vpn_list = self.request.data['vpn_user_name']
                custgroup_name = 'Anonymous_' + vpn_list.replace(';', '_')
                cust_tuple = models.ToraCustomer.objects.get_or_create(vpn_user_name=vpn_list,
                                                                        defaults={'custgroup_name': custgroup_name,
                                                                                'phone': self.request.data['vpn_phone'],
                                                                                'email': self.request.data['email'],
                                                                                'operator': self.request.user})
                customer_obj = cust_tuple[0]
            else:
                print("customer_id111:", self.request.data['customer'])
                customer_obj = models.ToraCustomer.objects.get(pk=self.request.data['customer'])
                custgroup_name = customer_obj.custgroup_name
            #groupname = customer_obj.custgroup_name
            #self.request.data['custgroup_name'] = custgroup_name
            print("self.request.data....:", self.request.data)
            print(type(self.request.user),type(customer_obj))
            logger.info("logger:" + str(self.request.user))
            if ('other_msg' in self.request.data.keys()):
                print("creating other_msg:", self.request.data['other_msg'])
            serializer.save(operator=self.request.user, customer=customer_obj, custgroup_name=custgroup_name)
        else:
            logger.info("不特殊处理提交数据")
            serializer.save(operator=self.request.user)

        


class TaskFlowDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.TaskFlow.objects.all()
    serializer_class = tora_ser.TaskFlow_Serializers
    permission_classes = (IsAuthenticated,)

    def perform_update(self, serializer):
        res = serializer.save(modify_oper=self.request.user)
        print("res:", res)
        #print("request.user:",self.request.user, type(self.request.user))
        #print(settings.DATABASES['default']['NAME'],settings.DATABASES['default']['PASSWORD'])
        #print("self.request:", self.request, type(self.request))
        print(self.request.data, type(self.request.data))
        task_data = self.request.data
        #流水任务完成
        if task_data["task_status"] == '1':
            print("发送更新信号")
            #signals.task_update.send(sender=models.TaskFlow, request=self.request)
        


class ToraServiceList(generics.ListCreateAPIView):
    queryset = models.ToraService.objects.all()
    serializer_class = tora_ser.ToraService_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('node_id', 'business')
    ordering_fields = ['node_id']
    #ordering = ['-id']


class ToraServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ToraService.objects.all()
    serializer_class = tora_ser.ToraService_Serializers
    permission_classes = (IsAuthenticated,)


class NodeInfoViewSet(viewsets.ModelViewSet):
    queryset = models.NodeInfo.objects.all()
    serializer_class = tora_ser.NodeInfo_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('engine_room', 'node_no')
    ordering_fields = ['create_time']
    #ordering = ['-id']


class TradeNodeViewSet(viewsets.ModelViewSet):
    queryset = models.TradeNode.objects.all()
    serializer_class = tora_ser.TradeNode_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('node', 'business', 'app_type')
    ordering_fields = ['create_time']
    #ordering = ['-id']


class ToraMqViewSet(viewsets.ModelViewSet):
    queryset = models.ToraMq.objects.all()
    serializer_class = tora_ser.ToraMq_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('ip_addr', 'business')
    ordering_fields = ['create_time']
    #ordering = ['-id']


class ToraMqGroupViewSet(viewsets.ModelViewSet):
    queryset = models.ToraMqGroup.objects.all()
    serializer_class = tora_ser.ToraMqGroup_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('mq_group_name', 'engine_room')
    ordering_fields = ['create_time']
    #ordering = ['-id']


class ShareServerInfoViewSet(viewsets.ModelViewSet):
    queryset = models.ShareServerInfo.objects.all()
    serializer_class = tora_ser.ShareServerInfo_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('engine_room', 'share_type')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    serializer_class = tora_ser.UserProfile_Serializers
    permission_classes = (IsAdminUser,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('user', 'phone')
    ordering_fields = ['phone']
    #ordering = ['-id']



class Login_rs(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        #logout(request)
        #return redirect(reverse("index"))
        #将token过期处理
        return Response({
            'data': 'success',
            # 自定义返回成功状态20000
            'code': 200
        })


class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        #logout(request)
        #return redirect(reverse("index"))
        #将token过期处理
        return Response({
            'data': 'success',
            # 自定义返回成功状态20000
            'code': 200
        })


class NodeDetailInfoViewSet(viewsets.ModelViewSet):
    queryset = models.NodeDetailInfo.objects.all()
    serializer_class = tora_ser.NodeDetailInfo_Serializers
    permission_classes = (IsAdminUser,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('node', 'business')
    ordering_fields = ['node']
    #ordering = ['-id']


class UpgradeTaskViewSet(viewsets.ModelViewSet):
    queryset = models.UpgradeTask.objects.all()
    serializer_class = tora_ser.UpgradeTask_Serializers
    permission_classes = (IsAdminUser,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('business', 'upgrade_version', 'task_status')
    ordering_fields = ['upgrade_version']
    #ordering = ['-id']

class AreaViewSet(viewsets.ModelViewSet):
    queryset = models.Area.objects.all()
    serializer_class = tora_ser.Area_Serializers
    #permission_classes = (IsAdminUser,)
    permission_classes = ()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('name', 'area_no')
    ordering_fields = ['area_no']
    #ordering = ['-id']


class ChoicesView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        Choices = tdc.get_choices()
        return Response(Choices)


class ToraFrontAddrView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        # tradeSet = models.TradeNode.objects.filter(Q(app_type='trade_front1') | Q(app_type='trade_front2') | \
        #                                     Q(app_type='trade_front3') | Q(app_type='trade_front4'))
        # result = []
        # for trade_obj in tradeSet:
        #     front_dict = model_to_dict(trade_obj)
        #     print(front_dict)
        get_sql = """
            SELECT nd.engine_room, nd.node_no, tn.business, app_type, sm.inner_ip, tn.port, internet_addr_ports, current_version
            From toraapp_nodeinfo as nd, toraapp_tradenode as tn, toraapp_shelfmachine as sm, toraapp_nodedetailinfo as ni
            Where tn.node_id = nd.id and app_type in ('trade_front1','trade_front2','trade_front3','trade_front4') 
                    and (tn.ip_addr = sm.high_trade_ip or tn.ip_addr = sm.inner_ip) and (ni.node_id = nd.id)
                    and (tn.business = ni.business)
            """
        res_data = tdc.executeOriginalsql(get_sql)
        return Response(res_data)

class QueryShareServerView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        print('request:', request)
        purpose = request.GET.get('purpose')
        engine_room = request.GET.get('engine_room')
        business = request.GET.get('business')
        print(purpose, engine_room, business)
        # 判断字段是否为空
        if purpose != None and business != None and engine_room != None:
            print("查找对应的服务器信息ing")
            resu = {'code': 200, 'message': 'getdata'}
            #business = 'hxzq|sp'
            tem_list = business.split('|')
            #bus_tup = tuple(tem_list)
            if len(tem_list)==1:
                bus_tup = "('" + str(tem_list[0]) + "')"
            else :
                bus_tup = str(tuple(tem_list))
            #查询共享服务器
            if purpose == '2':
                query_share_servers_info = "SELECT A.engine_room,A.node_id,A.os,A.os_version,A.cpu_model,A.cpu_cores,A.memory,A.disk_size,A.disk_type,A.inner_ip,A.outer_ip, C.assigned_count \
                        from toraapp_shelfmachine as A, toraapp_shareserverinfo as C where A.node_id in \
                        (select node_id from toraapp_tradenode \
                        where business in %s and app_type ='tradeserver1' group by node_id having count(business)=%d) \
                        and C.share_type = '%s' and C.engine_room = '%s' and A.id = C.machine_id and C.is_active = '1'" % (bus_tup,len(tem_list),purpose,engine_room)
            #查询可独用服务器
            elif purpose == '1':
                #暂时返回字段和共享是一样的
                query_share_servers_info = "SELECT A.engine_room,A.node_id,A.os,A.os_version,A.cpu_model,A.cpu_cores,A.memory,A.disk_size,A.disk_type,A.inner_ip,A.outer_ip, C.assigned_count \
                        from toraapp_shelfmachine as A, toraapp_shareserverinfo as C where A.node_id in \
                        (select node_id from toraapp_tradenode \
                        where business in %s and app_type ='tradeserver1' group by node_id having count(business)=%d) \
                        and C.share_type = '%s' and C.engine_room = '%s' and A.id = C.machine_id and C.is_active = '1'" % (bus_tup,len(tem_list),purpose,engine_room)
            #print('qerysql:',query_share_servers_info)
            res = tdc.executeOriginalsql(query_share_servers_info)
            print("resss:", res) 
            return Response(res)
        else:
            res_msg = 'purpose,engine_room,business不能为空！'
            logger.error(res_msg)
            raise serializers.ValidationError(res_msg)

    # def post(self,request):
    #     print('data:', request.data)
    #     #verify_data = BookSerialize(data=request.data)
    #     # if verify_data.is_valid():
    #     #     book = verify_data.save()
    #     #     return Response(verify_data.data)
    #     # else:
    #     #     return Response(verify_data.errors)
    #     server_data = {'code': 200, 'message': 'postdata'}
    #     return Response(server_data)

class GlobleParaViewSet(viewsets.ModelViewSet):
    queryset = models.GloblePara.objects.all()
    serializer_class = tora_ser.GloblePara_Serializers
    permission_classes = (IsAdminUser,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('para_name', 'id')
    ordering_fields = ['create_time']


class AccessApplyInfoViewSet(viewsets.ModelViewSet):
    queryset = models.AccessApplyInfo.objects.all()
    serializer_class = tora_ser.AccessApplyInfo_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('inner_ip', 'outer_ip', 'cur_status', 'customer_ip')
    ordering_fields = ['create_time']


class IsVpnExsitView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        engine_room = request.GET.get('engine_room')
        vpn_user_name = request.GET.get('vpn_user_name')
        vpn_phone = request.GET.get('vpn_phone')
        #Choices = tdc.get_choices()
        if vpn_user_name != None and engine_room != None and vpn_phone != None:
            if vpn_phone != '0':
                vpn_obj = models.VpnUserInfo.objects.filter(engine_room=engine_room,
                                                            vpn_user_name=vpn_user_name,
                                                            vpn_phone=vpn_phone)
            else:
                vpn_obj = models.VpnUserInfo.objects.filter(engine_room=engine_room,
                                                            vpn_user_name=vpn_user_name)

            if len(vpn_obj) == 0:
                is_exsit = 0
            else:
                is_exsit = 1

        else:
            res_msg = 'vpn_user_name,engine_room,vpn_phone不能为空！'
            logger.error(res_msg)
            raise serializers.ValidationError(res_msg)
        return Response(is_exsit)