import json
from json import decoder
from django.db.models.query import QuerySet
from django.http import response
from django.views.generic.base import View
from myapps.toraapp import serializers
from django.shortcuts import render
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django_apscheduler.models import DjangoJob, DjangoJobExecution
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
import myapps.tora_monitor.monitor_task as mtask
#from myapps.toraapp.tools import signals
from django.dispatch import receiver
from myapps.tora_monitor import mcallback
import socket
import sys
# sys.path.append('.')
#import monitor_task as mtask
import myapps.tora_monitor.models as mmodels
import myapps.tora_monitor.monitor_serializers as mserializers
import common.common_tools as ct
import os
import logging
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
import datetime
from common.mysql_tools_class import mysql_tools as mysqldc
import copy
from django.conf import settings
logger = logging.getLogger('django')

db_info=[settings.DATABASES["default"]["HOST"],settings.DATABASES["default"]["USER"],
settings.DATABASES["default"]["PASSWORD"],settings.DATABASES["default"]["NAME"],settings.DATABASES["default"]["PORT"]]

# Create your views here.


# class ToraMonitorViewSet(viewsets.ModelViewSet):
#     queryset = models.ShareServerInfo.objects.all()
#     serializer_class = tora_ser.ShareServerInfo_Serializers
#     permission_classes = (IsAuthenticated,)
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ('node', 'mq_name', 'business', 'app_type')
#     ordering_fields = ['create_time']
#     ordering = ['id']

#     def perform_create(self, serializer):
#         serializer.save(operator=self.request.user)


def process_monitorJob(process_type, ObjectJob):
    print("process_monitorJob was called!")
    try:
        print("scheduler:", scheduler)
    except NameError as e:
        print("scheduler异常")
        print(type(e))
        return -1
    if process_type == 'add':
        logger.info("add job:" + ObjectJob.job_id + "定时函数：" + str(ObjectJob.job_func))
        #增加任务
        # # 在每天22点，每隔 1分钟 运行一次 job 方法
        # scheduler.add_job(job, 'cron', hour=22, minute='*/1', args=['job1'])
        # # 在每天22和23点的25分，运行一次 job 方法
        # scheduler.add_job(job, 'cron', hour='22-23', minute='25', args=['job2'])
        func_str = 'mtask.' + ObjectJob.job_func
        # call_func = eval(func_str)
        if ObjectJob.job_args:
            add_job_args = ObjectJob.job_args + ';' + ObjectJob.job_id
            args = add_job_args.split(';')
        else:
            args = [ObjectJob.job_id]
        if ObjectJob.trigger == 'cron':
            scheduler.add_job(func=eval(func_str), args=args, id=ObjectJob.job_id, trigger='cron',
                            month=ObjectJob.month, day=ObjectJob.day, week=ObjectJob.week, day_of_week=ObjectJob.day_of_week, 
                            hour=ObjectJob.hour, minute=ObjectJob.minute, second=ObjectJob.second, 
                            start_date=ObjectJob.start_date, end_date=ObjectJob.end_date, 
                            replace_existing=True)
        elif ObjectJob.trigger == 'interval':
            def int_map(para):
                if para == None:
                    return 0
                return int(para)
            print("ObjectJob.minute: ", ObjectJob.minute)
            scheduler.add_job(func=eval(func_str), args=args, id=ObjectJob.job_id, trigger='interval',
                            days=int_map(ObjectJob.day), weeks=int_map(ObjectJob.week), hours=int_map(ObjectJob.hour), minutes=int_map(ObjectJob.minute), 
                            seconds=int_map(ObjectJob.second), start_date=ObjectJob.start_date, end_date=ObjectJob.end_date, 
                            replace_existing=True)
        elif ObjectJob.trigger == 'date':
            scheduler.add_job(func=eval(func_str), args=args, id=ObjectJob.job_id, trigger='date',
                            run_date=ObjectJob.start_date, replace_existing=True)
        else:
            print("Not support")
    elif process_type == 'resume':
        logger.info("resume job:" + ObjectJob.job_id)
        res = scheduler.resume_job(ObjectJob.job_id)
        return res
    elif process_type == 'pause':
        logger.info("pause job:" + ObjectJob.job_id)
        res = scheduler.pause_job(ObjectJob.job_id)
        return res
    elif process_type == 'remove':
        logger.info("remove job:" + ObjectJob.job_id)
        res = scheduler.remove_job(ObjectJob.job_id)
        return res
    elif process_type == 'modify':
        logger.info("modify job:" + ObjectJob.job_id + "函数参数： " + str(ObjectJob.args))
        res = scheduler.modify_job(ObjectJob.job_id, args=ObjectJob.args)
        return res
    else:
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        logger.error("process_type参数错误")
        return 0


def update_jobs_status():
    job_ids = DjangoJob.objects.all()
    for job in job_ids:
        print(job.id)
        job_exeobj = DjangoJobExecution.objects.filter(job_id=job.id).latest('id')
        print(job_exeobj.id, job_exeobj.run_time, job_exeobj.status)


def zt_getmonitorip():
    '''
    获取需要监控的ip列表
    后期直接关联监控表的后端ip
    '''
    results=[]
    try:
        # sql="SELECT ipmi_ip from tora_oper_data.tora_monitor_ipmimonitorip where monitor_flag=1;"
        sql="SELECT ipmi_ip from tora_oper_data.toraapp_shelfmachine where is_active=1;"
        myconnect= mysqldc(db_info)
        getAllDataByIpmiIp,nil= myconnect.get_db_data(sql)
        if getAllDataByIpmiIp:
            for i in getAllDataByIpmiIp:
                if i[0] != None and i[0] != 'null' and i[0] !='':
                    results.append(i[0])
    except:
        print('get monitor ip error')
        pass
    return results


class MonitorJobViewSet(viewsets.ModelViewSet):
    queryset = mmodels.MonitorJob.objects.all()
    serializer_class = mserializers.MonitorJob_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('job_id', 'trigger', 'is_active', 'day', 'hour', 'minute')
    ordering_fields = ['id']
    ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save()
        print("request.user:",self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        req_data = self.request.data
        print("req_data:", req_data)

    def list(self, request, *args, **kwargs):
        print("先去更新记录，再返回结果")
        #update_jobs = update_jobs_status()
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DiskMonitorDataViewSet(viewsets.ModelViewSet):
    queryset = mmodels.DiskMonitorData.objects.all()
    serializer_class = mserializers.DiskMonitorData_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('inner_ip', 'file_dir')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)    


class MemMonitorDataViewSet(viewsets.ModelViewSet):
    queryset = mmodels.MemMonitorData.objects.all()
    serializer_class = mserializers.MemMonitorData_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('inner_ip',)
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)    

class NodeTradeInfoViewSet(viewsets.ModelViewSet):
    queryset = mmodels.NodeTradeInfo.objects.all()
    serializer_class = mserializers.NodeTradeInfo_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('business','node_no','engine_room')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)   


class SmsControlDataViewSet(viewsets.ModelViewSet):
    queryset = mmodels.SmsControlData.objects.all()
    serializer_class = mserializers.SmsControlData_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('init_day','total_used_count')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)   

class SmsRecordDataViewSet(viewsets.ModelViewSet):
    queryset = mmodels.SmsRecordData.objects.all()
    serializer_class = mserializers.SmsRecordData_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('sms_type','send_phones')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)   

class ToraDatabaseMonitorCfgViewSet(viewsets.ModelViewSet):
    queryset = mmodels.ToraDatabaseMonitorCfg.objects.all()
    serializer_class = mserializers.ToraDatabaseMonitorCfg_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('node_no','update_time')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)  
		
class ipmiInfoDataViewSet(viewsets.ModelViewSet):
    queryset = mmodels.ipmiInfoData.objects.all()
    serializer_class =mserializers.ipmiInfoData_Serializers

    @action(methods=["GET"], detail=True)
    def getsinglealldata(self,request,pk):
        """
            通过id获取ipmi_ip,在筛选出此ipmi_ip 对应10天内所有监控信息
        """
        nowdate=datetime.datetime.now()
        offsset = datetime.timedelta(days=-10)
        redate=nowdate+offsset
        getDataByID = self.get_queryset().get(pk=pk)
        getAllDataByIpmiIp=mmodels.ipmiInfoData.objects.filter(ipmi_ip=getDataByID.ipmi_ip,check_time__gt=redate)
        serilizer = self.get_serializer(instance=getAllDataByIpmiIp,many=True)
        # print(len(serilizer.data))
        return Response(serilizer.data)

    @action(methods=["GET"], detail=True)
    def getsinglebaseline(self,request,pk):
        """
            通过id获取ipmi_ip,在筛选出此ipmi_ip的基准信息
            如果没有设置基准，则选择30天前的一个数据为基准
        """
        nowdate=datetime.datetime.now()
        offsset = datetime.timedelta(days=-30)
        redate=nowdate+offsset
        getDataByID = self.get_queryset().get(pk=pk)
        getAllDataByIpmiIp=mmodels.ipmiInfoData.objects.filter(ipmi_ip=getDataByID.ipmi_ip,baseline_flag=True)
        if not getAllDataByIpmiIp:
            getAllDataByIpmiIp=mmodels.ipmiInfoData.objects.filter(ipmi_ip=getDataByID.ipmi_ip,check_time__gt=redate).order_by("check_time").all()
        serilizer = self.get_serializer(instance=getAllDataByIpmiIp,many=True)
        return Response(serilizer.data[0])

    @action(methods=["GET"], detail=False)
    def getipmirecently(self,request):
        """
            获取最近一次的监控信息
        """
        basemodel={"ipmi_ip":'', "cpu1": 0, "cpu2": 0, "cpu3": 0, "cpu4": 0,
    "fan1": 0, "fan2": 0, "fan3": 0, "fan4": 0, "fan5": 0, "fan6": 0, "fan7": 0, "fan8": 0, "fan9": 0, "fan10": 0, "fan11": 0, "fan12": 0, "fan13": 0, "fan14": 0, "fan15": 0, "fan16": 0, "check_time":''}
        sql='''
        SELECT check_time,COUNT(1) AS count from tora_oper_data.tora_monitor_ipmiinfodata GROUP BY check_time ORDER BY check_time desc LIMIT 2;
        '''
        myconnect= mysqldc(db_info)
        getalltime,nil= myconnect.get_db_data(sql)
        datacheck=[]
        results=[]
        iplist= zt_getmonitorip()
        for i in getalltime:
            if datacheck == []:
                datacheck.append(i[0])
                datacheck.append(i[1])
            elif( datacheck[1] < i[1]):
                datacheck.append(i[0])
                datacheck.append(i[1])
        getAllDataBychecktime=mmodels.ipmiInfoData.objects.filter(check_time=datacheck[0], ipmi_ip__in=iplist ).order_by('-cpu1_temp')
        serilizer = self.get_serializer(instance=getAllDataBychecktime,many=True)
        # for oneip in zt_getmonitorip():
        #     flag=0
        #     for item in serilizer.data:
        #         if item["ipmi_ip"] == oneip:
        #             flag=1
        #             results.append(item)
        #             break
        #     if flag == 0:
        #         setIPdata = copy.deepcopy(basemodel)
        #         setIPdata["ipmi_ip"] = oneip
        #         results.append(setIPdata)
        return Response(serilizer.data)

    @action(methods=["GET"], detail=False)
    def getmonitorip(self,request):
        """
            获取需要监控的ip列表
        """
        results=zt_getmonitorip()
        return Response(results)
    
    @action(methods=["GET"], detail=False)
    def getmonitorchecktime(self,request):
        """
            获取10天监控时间戳
        """
        results=[]
        try:
            sql="SELECT distinct(check_time) FROM tora_oper_data.tora_monitor_ipmiinfodata where DATE_SUB(CURDATE(), INTERVAL 10 DAY) <= date(check_time);"
            myconnect= mysqldc(db_info)
            getchecktime,nil= myconnect.get_db_data(sql)
            if getchecktime:
                for i in getchecktime:
                    results.append(i[0])
        except:
            print('get monitor check time  error')
            pass
        return Response(results)
    
    @action(methods=["GET"], detail=False)
    def getallbaseline(self,request):
        """
            按监控ip 筛选出所有设置baseline_flag=True的基准信息, 如果没有则取30天前最近的数据为基准
            todo:没设置baseline_flag=True的情况下速度较慢，需要优化
        """
        # nowdate=datetime.datetime.now()
        # offsset = datetime.timedelta(days=-30)
        # redate=nowdate+offsset
        # ipresults=[]
        # alldata=[]
        # try:
        #     ipresults=zt_getmonitorip()
        # except:
        #     ipresults=[]
        # for oneip in ipresults:
        #     getonedata=mmodels.ipmiInfoData.objects.filter(ipmi_ip=oneip,baseline_flag=True)
        #     if not getonedata:
        #         getonedata=mmodels.ipmiInfoData.objects.filter(ipmi_ip=oneip,check_time__gt=redate).order_by("check_time").all()
        #     serilizer = self.get_serializer(instance=getonedata,many=True)
        #     alldata.append(serilizer.data[0])
        # print('getallbaseline use time: ',(datetime.datetime.now()-nowdate))
        # return Response(alldata)

        iplist= zt_getmonitorip()
        getonedata=mmodels.ipmiInfoData.objects.filter(ipmi_ip__in=iplist,baseline_flag=True).order_by("-cpu1_temp")
        serilizer = self.get_serializer(instance=getonedata,many=True)
        return Response(serilizer.data)
        
    @action(methods=["POST"], detail=False,url_path="search")
    def ipmisearch(self,request):
        '''
        搜索api，按条件搜索结果，并返回
        '''
        result_query=''
        data_ipmi_ip= ''
        data_cpu_fan= ''
        dict_data = json.loads(request.body.decode())
        ipmi_ip = dict_data.get('ipmi_ip')
        cpu_temp = dict_data.get('cpu_temp')
        fan_sp = dict_data.get('fan_sp')
        checktimeStart = dict_data.get('checktimeStart')
        checktimeEnd = dict_data.get('checktimeEnd')
        if (ipmi_ip != '' and ipmi_ip != None):
            data_ipmi_ip=mmodels.ipmiInfoData.objects.filter(ipmi_ip__icontains=ipmi_ip,
            check_time__gte = checktimeStart,check_time__lte =checktimeEnd ).order_by("-check_time")
        data_cpu_fan =mmodels.ipmiInfoData.objects.filter(cpu1_temp__gte = cpu_temp,fan1_sp__lte = fan_sp,
        check_time__gte = checktimeStart,check_time__lte =checktimeEnd ).order_by("-check_time") 
        
        iplist= zt_getmonitorip()
        getdatabymonitorip = mmodels.ipmiInfoData.objects.filter(ipmi_ip__in=iplist)

        if (data_ipmi_ip != ''):
            result_query = data_ipmi_ip & data_cpu_fan & getdatabymonitorip
        else:
            result_query = data_cpu_fan & getdatabymonitorip
        serilizer = self.get_serializer(instance=result_query,many=True)
        return Response(serilizer.data)


class FpgaMonitorDataViewSet(viewsets.ModelViewSet):
    queryset = mmodels.FpgaMonitorData.objects.all()
    serializer_class = mserializers.FpgaMonitorData_Serializers
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('inner_ip','para_name','para_value')
    ordering_fields = ['create_time']
    #ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)  



job_defaults = {
    'coalesce': False,
    'max_instances': 5
}


#解决uwsgi多线程重复运行job
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 47200))
except socket.error:
    print("!!!scheduler already started, DO NOTHING")
else:
    # from apscheduler.schedulers.background import BackgroundScheduler
    # scheduler = BackgroundScheduler()
    # scheduler.start()
    # print "scheduler started"

    #启动scheduler
    try:
        # 实例化调度器
        scheduler = BackgroundScheduler(job_defaults=job_defaults)
        # 调度器使用默认的DjangoJobStore()
        scheduler.add_jobstore(DjangoJobStore(), 'default')
        print("begaining:", scheduler.get_jobs())
        # 注册定时任务并开始
        register_events(scheduler)
        scheduler.start()
        jobs = scheduler.get_jobs()
        print("begaining222:",scheduler.get_jobs())
    except Exception as e:
        logger.error("启动scheduler异常：" + str(e))
        # 有错误就停止定时器
        scheduler.shutdown()