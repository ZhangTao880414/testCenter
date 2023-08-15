from django.dispatch import receiver
from django.db.models import signals
from myapps.tora_monitor import models as mmodels
from myapps.tora_monitor import views as mviews
from django.contrib.auth.models import User
from django.core.mail import send_mail
import copy
import common.common_tools as ct
import common.tora_django_common as tdc
from apscheduler.schedulers.background import BackgroundScheduler
import logging
logger = logging.getLogger('django')


#增加修改MonitorJob时操作
@receiver(signals.post_init, sender=mmodels.MonitorJob)
def modify_monitorJob_post_init(sender, instance, **kwargs):
    print("instance.is_active111:", instance.is_active)
    instance.__original_name = instance.is_active
 
@receiver(signals.post_save, sender=mmodels.MonitorJob)
def modify_monitorJob(sender, instance, created, **kwargs):
    print("instance.is_active2:", instance.is_active)
    if created:
        if instance.is_active == '1':
            print("新增监控项")
            print("instance:", type(instance), instance)
            mviews.process_monitorJob('add', instance)
    elif not created and instance.__original_name != instance.is_active: 
        #print("job:",scheduler.get_jobs()) 
        if instance.is_active == '1':
            print("do监控项激活")
            #print(mviews.scheduler.get_jobs())
            print("instance:", type(instance), instance)
            print("instance:", type(instance), instance.job_args)
            res = mviews.process_monitorJob('resume', instance)
            print("resume_call_res:", res)
        else:
            print("do监控项停止")
            #print(mviews.scheduler.get_jobs())
            #mviews.print_job()
            print("instance:", type(instance), instance.job_args)
            res = mviews.process_monitorJob('pause', instance)
            print("pause_call_res:", res)

#删除MonitorJob时触发
@receiver(signals.post_delete, sender=mmodels.MonitorJob)
def delete_monitorJob(sender, instance, **kwargs):
    print("instance: ", instance)
    print("删除监控项")
    mviews.process_monitorJob('remove', instance)


# @receiver(monitor_job_update)
# def monitor_job_update_callback(sender, **kwargs):
#     try:
#         print("更新监控任务")
#     except Exception:
#         err_msg = 'Faild to run monitor_job_update_callback!'
#         logger.error(err_msg, exc_info=True)
#         ct.send_sms_control('NoLimit', err_msg, '13681919346')