from django.db import models
from django_apscheduler.models import DjangoJob, DjangoJobExecution
import common.tora_django_common as tdc
# Create your models here.



# STATUS_CHOICES = (
#     (u'0', u'未激活'),
#     (u'1', u'正常'),
# )

# TRIGGER_CHOICES = (
#     (u'date', u'一次性'),
#     (u'interval', u'固定间隔'),
#     (u'cron', u'crontab格式'),
# )
Choices = tdc.get_choices()
STATUS_CHOICES = tdc.dict2tuple(Choices['tora_monitor']['STATUS_CHOICES'])
TRIGGER_CHOICES = tdc.dict2tuple(Choices['tora_monitor']['TRIGGER_CHOICES'])

class MonitorJob(models.Model):
    job_id = models.CharField(verbose_name='任务标识', max_length=100, unique=True)
    trigger = models.CharField(verbose_name='触发类型', max_length=20, choices=TRIGGER_CHOICES, default='cron')
    job_func = models.CharField(verbose_name='任务函数', max_length=40)
    job_args = models.CharField(verbose_name='任务参数', max_length=40, null=True, blank=True)
    month = models.CharField(verbose_name='月(1-12)', max_length=40, null=True, blank=True)
    day = models.CharField(verbose_name='日(1-31)', max_length=40, null=True, blank=True)
    week = models.CharField(verbose_name='周(1-53)', max_length=40, null=True, blank=True)
    day_of_week = models.CharField(verbose_name=' 周内第几天或者星期几', max_length=40, null=True, blank=True)
    hour = models.CharField(verbose_name=' 小时', max_length=40, null=True, blank=True)
    minute = models.CharField(verbose_name='分', max_length=40, null=True, blank=True)
    second = models.CharField(verbose_name='秒', max_length=40, null=True, blank=True)
    start_date = models.DateTimeField(verbose_name='最早开始日期', null=True, blank=True)
    end_date = models.DateTimeField(verbose_name='最晚结束日期', null=True, blank=True)
    is_active = models.CharField(verbose_name='当前状态', max_length=2, choices=STATUS_CHOICES, default='1')
    comment = models.CharField(verbose_name='任务说明', max_length=254, blank=True, null=True)
    last_status = models.CharField(verbose_name='最新监控结果', max_length=40, null=True, blank=True)
    last_runtime = models.DateTimeField(verbose_name='最后执行时间', null=True, blank=True)
    monitor_data = models.TextField(verbose_name='监控返回数据', blank=True, null=True)

    def __str__(self):
        return self.job_id

    class Meta:
        verbose_name = "监控任务"
        verbose_name_plural = verbose_name
        #unique_together = (('job_name'),)
