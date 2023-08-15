
# -*- coding: utf-8 -*-

from django.conf import settings
import django
import os
import sys
sys.path.extend(['D:\\my_project\\python3\\django_project\\ToraOps_project\\ToraOps'])
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ToraOps.settings')
django.setup()

from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import monitor_task as mtask
import time, threading
from datetime import datetime


# url="mysql+pymysql://singularity_oper:Singularity$20201113@192.168.238.21/django_test?charset=utf8"
# #job.scheduler.add_jobstore(jobstore="sqlalchemy",url=url,tablename='api_job')

# jobstores = {
#     #'mongo': MongoDBJobStore(),
#     #'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
#     'default': SQLAlchemyJobStore(url=url, tablename='django_apscheduler_djangojob',engine='django.db.backends.mysql')
# }
# executors = {
#     'default': ThreadPoolExecutor(20),
#     'processpool': ProcessPoolExecutor(5)
# }
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
# scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)


def job():
    #print('job 3s')
    #print('job thread_id-{0}, process_id-{1}'.format(threading.get_ident(), os.getpid()))
    #time.sleep(50)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

try:
    # 实例化调度器
    scheduler = BackgroundScheduler(job_defaults=job_defaults)
    # 调度器使用默认的DjangoJobStore()
    scheduler.add_jobstore(DjangoJobStore(), 'default')
    print(scheduler.get_jobs())
    print(os.getcwd())

    # 每天8点半执行这个任务
    # @register_job(scheduler, "interval", args=['zhangwei'], seconds=3, id='test_job', replace_existing=True)
    # def test(a):
    #     # 具体要执行的代码
    #     #mtask.test_job()
    #     print("I am test job by " + a)
    scheduler.add_job(func=mtask.test_job, id='test_job1', trigger='interval', seconds=3,
                          replace_existing=True)
    # scheduler.add_job(func=job, id='test_job1', trigger='cron', hour='8-16', minute='23,24,25,26', 
    #                       replace_existing=True)

    #mtask.test_job()
    # def test():
    #     # 具体要执行的代码
    #     mtask.test_job()
        #print("I am test job")
    # @register_job(scheduler, 'cron', day_of_week='mon-fri', hour='15', minute='55', second='10,20,30',id='task_time')
    # def test_job():
    #   t_now = time.localtime()
    #   print(t_now)
    # 注册定时任务并开始
    register_events(scheduler)

    scheduler.start()
    print("Scheduler started!")
    while(True):
        print('main 1s')
        time.sleep(1)
    # try:
    #     # This is here to simulate application activity (which keeps the main thread alive).
    #     while True:
    #         time.sleep(2)
        
    # except (KeyboardInterrupt, SystemExit):
    #     # Not strictly necessary if daemonic mode is enabled but should be done if possible
    #     scheduler.shutdown()
    
except Exception as e:
    print(e)
    # 有错误就停止定时器
    scheduler.shutdown()