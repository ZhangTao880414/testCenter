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
logger = logging.getLogger('django')


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
        looger.error("process_type参数错误")
        return 0


def update_jobs_status():
    job_ids = DjangoJob.objects.all()
    for job in job_ids:
        print(job.id)
        job_exeobj = DjangoJobExecution.objects.filter(job_id=job.id).latest('id')
        print(job_exeobj.id, job_exeobj.run_time, job_exeobj.status)




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