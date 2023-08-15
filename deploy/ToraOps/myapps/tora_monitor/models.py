from logging import fatal
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
BUSINESS_CHOICES = tdc.dict2tuple(Choices['toraapp']['BUSINESS_CHOICES'])
ROOM_CHOICES = tdc.dict2tuple(Choices['toraapp']['ROOM_CHOICES'])
COM_STATUS = tdc.dict2tuple(Choices['toraapp']['COM_STATUS'])
BOOLEAN_CHOICES = tdc.dict2tuple(Choices['toraapp']['BOOLEAN_CHOICES'])


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


class DiskMonitorData(models.Model):
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP')
    file_dir = models.CharField(verbose_name='目录', max_length=40, default='/')
    total_size = models.FloatField(verbose_name='总量(G)', max_length=20, default=0)
    used_size = models.FloatField(verbose_name='已使用量(G)', max_length=20, default=0)
    avail_size = models.FloatField(verbose_name='可用量(G)', max_length=20, default=0)
    usage = models.FloatField(verbose_name='使用率(%)', max_length=20, default=0)
    mounted_on = models.CharField(verbose_name='挂载盘', max_length=20, default='/')
    is_warning = models.CharField(verbose_name='是否需要报警', max_length=2, choices=BOOLEAN_CHOICES, default='0')
    is_handled = models.CharField(verbose_name='是否已处理', max_length=2, choices=BOOLEAN_CHOICES, default='0')
    send_phone = models.CharField(verbose_name='接收警告的手机号', max_length=254, blank=True, null=True)
    send_mail = models.CharField(verbose_name='接收警告的邮箱', max_length=254, blank=True, null=True)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return self.inner_ip

    class Meta:
        verbose_name = "磁盘使用监控数据"
        verbose_name_plural = verbose_name


class MemMonitorData(models.Model):
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP')
    total_mem = models.FloatField(verbose_name='总内存(G)', max_length=10, default=0)
    used_mem = models.FloatField(verbose_name='已使用量(G)', max_length=10, default=0)
    usage = models.FloatField(verbose_name='已使用率(%)', max_length=10, default=0)
    is_warning = models.CharField(verbose_name='是否需要报警', max_length=2, choices=BOOLEAN_CHOICES, default='0')
    is_handled = models.CharField(verbose_name='是否已处理', max_length=2, choices=BOOLEAN_CHOICES, default='0')
    send_phone = models.CharField(verbose_name='接收警告的手机号', max_length=254, blank=True, null=True)
    send_mail = models.CharField(verbose_name='接收警告的邮箱', max_length=254, blank=True, null=True)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return self.inner_ip

    class Meta:
        verbose_name = "内存使用监控数据"
        verbose_name_plural = verbose_name


# class CPUTempMonitorData(models.Model):
#     # machine = models.OneToOneField("ShelfMachine", verbose_name='服务器信息', on_delete=models.CASCADE)
#     inner_ip = models.GenericIPAddressField(verbose_name='内网IP')
#     ipmi_ip = models.GenericIPAddressField(verbose_name='管理口IP')
#     total_mem = models.CharField(verbose_name='总内存', max_length=40)
#     used_mem = models.CharField(verbose_name='已使用量', max_length=40)
#     usage = models.CharField(verbose_name='已使用率', max_length=40)
#     is_warning = models.CharField(verbose_name='是否需要报警', max_length=2, choices=STATUS_CHOICES, default='0')
#     is_handled = models.CharField(verbose_name='是否已处理', max_length=2, choices=STATUS_CHOICES, default='0')
#     send_phone = models.CharField(verbose_name='接收警告的手机号', max_length=254, blank=True, null=True)
#     send_mail = models.CharField(verbose_name='接收警告的邮箱', max_length=254, blank=True, null=True)
#     comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
#     create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
#     update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

#     def __str__(self):
#         return self.inner_ip

#     class Meta:
#         verbose_name = "内存使用监控数据"
#         verbose_name_plural = verbose_name


class NodeTradeInfo(models.Model):
    engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    business = models.CharField(verbose_name='业务', max_length=20, choices=BUSINESS_CHOICES)
    node_no = models.CharField(verbose_name='节点编号', max_length=4, unique=True)
    cur_status = models.CharField(verbose_name='当前状态', max_length=2, choices=COM_STATUS, default='1')
    online_cust_count = models.IntegerField(verbose_name='在线用户数', blank=True, null=True)
    order_count = models.IntegerField(verbose_name='委托笔数', blank=True, null=True)
    cancel_count = models.IntegerField(verbose_name='撤单笔数', blank=True, null=True)
    trade_count = models.IntegerField(verbose_name='成交笔数', blank=True, null=True)
    turnover = models.FloatField(verbose_name='成交金额', blank=True, null=True)
    tora_version = models.CharField(verbose_name='奇点版本信息', max_length=20, blank=True, null=True)
    start_time = models.DateTimeField(verbose_name='启动时间', auto_now_add=True)
    stop_time = models.DateTimeField(verbose_name='关闭时间', auto_now_add=True)
    error_msg = models.CharField(verbose_name='异常信息', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    
    def __str__(self):
        return self.node_no

    class Meta:
        verbose_name = "节点交易监控信息"
        verbose_name_plural = verbose_name
        ordering = ['-id']


class SmsControlData(models.Model):
    init_day = models.DateField(verbose_name='初始化日期')
    ps_port = models.IntegerField(verbose_name='进程端口监控已用', default=0)
    disk = models.IntegerField(verbose_name='硬盘监控已发', default=0)
    mem = models.IntegerField(verbose_name='内存监控已发', default=0)
    ping = models.IntegerField(verbose_name='ping监控已发', default=0)
    db_trade = models.IntegerField(verbose_name='数据库盘中监控已发', default=0)
    core = models.IntegerField(verbose_name='core监控已发', default=0)
    errorID = models.IntegerField(verbose_name='errorID监控已发', default=0)
    errorlog = models.IntegerField(verbose_name='errorlog监控已发', default=0)
    ipmi = models.IntegerField(verbose_name='ipmi监控已发', default=0)
    NoLimit = models.IntegerField(verbose_name='NoLimit已发', default=0)
    total_used_count = models.IntegerField(verbose_name='当日已用总量', default=0)
    single_limit = models.IntegerField(verbose_name='单项限制次数', default=20)
    total_limit = models.IntegerField(verbose_name='每日总限量', default=500)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return str(self.init_day)

    class Meta:
        verbose_name = "短信发送数量配置"
        verbose_name_plural = verbose_name


class ToraDatabaseMonitorCfg(models.Model):
    business = models.CharField(verbose_name='业务', max_length=20, choices=BUSINESS_CHOICES)
    node_no = models.CharField(verbose_name='节点编号', max_length=4)
    is_monitor = models.CharField(verbose_name='是否监控', max_length=2, choices=BOOLEAN_CHOICES, default='1')
    cur_status = models.CharField(verbose_name='当前状态', max_length=2, choices=COM_STATUS, default='1')
    AppInfo = models.IntegerField(verbose_name='组件行数', blank=True, null=True)
    AppRunningInfo = models.IntegerField(verbose_name='数据库项', blank=True, null=True)
    DbmtIbfo = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    Exchange = models.CharField(verbose_name='证券交易所ExchangeOrderNo', max_length=50, blank=True, null=True)
    ExchangeSyncStatus = models.CharField(verbose_name='DateSyncStatus(3/4/4)', max_length=50, blank=True, null=True)
    Front = models.IntegerField(verbose_name='前端连接数', blank=True, null=True)
    FundTransferDetail = models.CharField(verbose_name='StatusMsg处理状态', max_length=50, blank=True, null=True)
    OrderLocalSeqPrefix = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEBondConversionInfo = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEBondPutbackInfo = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEETFBasket = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEETFFile = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEIPOInfo = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEInvestorPositionLimit = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEInvestorTradingFee = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEPBU = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEPosition = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEPositionLimitTemplate = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSEPositionParam = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSESecurity = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSETrader = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSETraderOffer = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSETradingFee = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSETradingFeeLimitTemplate = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSETradingFeeTemplate = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SSETradingRightTemplate = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    SystemParam = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    TerminalFloatingCommission = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    TradingAccount = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    TransNum_Trading = models.CharField(verbose_name='盘钟transnum', max_length=50, blank=True, null=True)
    XMDserver = models.CharField(verbose_name='数据库项', max_length=50, blank=True, null=True)
    TransNum_Closed = models.CharField(verbose_name='盘后transnum', max_length=50, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    
    def __str__(self):
        return self.node_no

    class Meta:
        verbose_name = "奇点数据库日常监控项"
        verbose_name_plural = verbose_name
        ordering = ['-id']
        unique_together = (('business','node_no'),)


class SmsRecordData(models.Model):
    sms_type = models.CharField(verbose_name='短信类型', max_length=32)
    send_msg = models.CharField(verbose_name='发送内容', max_length=254, blank=True, null=True)
    send_phones = models.CharField(verbose_name='发送的手机号', max_length=254, blank=True, null=True)
    send_status = models.CharField(verbose_name='发送状态', max_length=2, choices=BOOLEAN_CHOICES, default='1')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return self.sms_type

    class Meta:
        verbose_name = "短信发送记录"
        verbose_name_plural = verbose_name

# class ipmimonitorip(models.Model):
#     ipmi_ip = models.GenericIPAddressField(verbose_name='管理口IP')
#     monitor_flag = models.BooleanField(verbose_name='监控状态',blank=True,default=True)
#     ignore_flag = models.BooleanField(verbose_name='忽略告警',blank=True,default=False)
#     def __str__(self):
#         return self.ipmi_ip
#     class Meta:
#         verbose_name = "IPMI监控IP"
#         verbose_name_plural = verbose_name

class ipmiInfoData(models.Model):
    ipmi_ip = models.GenericIPAddressField(verbose_name='管理口IP')
    cpu1_temp = models.FloatField(verbose_name='cpu1温度', max_length=40,blank=True, null=True)
    cpu2_temp = models.FloatField(verbose_name='cpu2温度', max_length=40,blank=True, null=True)
    cpu3_temp = models.FloatField(verbose_name='cpu3温度', max_length=40,blank=True, null=True)
    cpu4_temp = models.FloatField(verbose_name='cpu4温度', max_length=40,blank=True, null=True)
    fan1_sp = models.FloatField(verbose_name='风扇1速度', max_length=60,blank=True, null=True)
    fan2_sp = models.FloatField(verbose_name='风扇2速度', max_length=60,blank=True, null=True)
    fan3_sp = models.FloatField(verbose_name='风扇3速度', max_length=60,blank=True, null=True)
    fan4_sp = models.FloatField(verbose_name='风扇4速度', max_length=60,blank=True, null=True)
    fan5_sp = models.FloatField(verbose_name='风扇5速度', max_length=60,blank=True, null=True)
    fan6_sp = models.FloatField(verbose_name='风扇6速度', max_length=60,blank=True, null=True)
    fan7_sp = models.FloatField(verbose_name='风扇7速度', max_length=60,blank=True, null=True)
    fan8_sp = models.FloatField(verbose_name='风扇8速度', max_length=60,blank=True, null=True)
    fan9_sp = models.FloatField(verbose_name='风扇9速度', max_length=60,blank=True, null=True)
    fan10_sp = models.FloatField(verbose_name='风扇10速度', max_length=60,blank=True, null=True)
    fan11_sp = models.CharField(verbose_name='风扇11速度', max_length=60,blank=True, null=True)
    fan12_sp = models.FloatField(verbose_name='风扇12速度', max_length=60,blank=True, null=True)
    fan13_sp = models.FloatField(verbose_name='风扇13速度', max_length=60,blank=True, null=True)
    fan14_sp = models.FloatField(verbose_name='风扇14速度', max_length=60,blank=True, null=True)
    fan15_sp = models.FloatField(verbose_name='风扇15速度', max_length=60,blank=True, null=True)
    fan16_sp = models.FloatField(verbose_name='风扇16速度', max_length=60,blank=True, null=True)
    check_time = models.DateTimeField(verbose_name='检测时间', blank=True, null=True)
    baseline_flag = models.BooleanField(verbose_name='设为基准',blank=True,null=True,default=False)
    origin_data = models.TextField(verbose_name='原始数据',blank=True,null=True)

    def __str__(self):
        return self.ipmi_ip

    class Meta:
        verbose_name = "IPMI硬件监控详情"
        verbose_name_plural = verbose_name


class FpgaMonitorData(models.Model):
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP')
    para_name = models.CharField(verbose_name='参数名称', max_length=50, blank=True, null=True)
    para_type = models.CharField(verbose_name='参数类型', max_length=50, blank=True, null=True)
    para_value = models.CharField(verbose_name='参数值', max_length=254, blank=True, null=True)
    bound = models.CharField(verbose_name='是否约束', max_length=2, choices=BOOLEAN_CHOICES, default='1')
    start_time = models.CharField(verbose_name='开始监控时间', max_length=10, blank=True, null=True)
    end_time = models.CharField(verbose_name='开始监控时间', max_length=10, blank=True, null=True)
    lower_limit = models.CharField(verbose_name='阀值下限', max_length=20, blank=True, null=True)
    upper_limit = models.CharField(verbose_name='阀值上限', max_length=20, blank=True, null=True)
    increment = models.CharField(verbose_name='是否增长', max_length=2, choices=BOOLEAN_CHOICES, default='0')
    is_warning = models.CharField(verbose_name='是否需要报警', max_length=2, choices=BOOLEAN_CHOICES, default='0')
    is_handled = models.CharField(verbose_name='是否已处理', max_length=2, choices=BOOLEAN_CHOICES, default='0')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return self.para_name

    class Meta:
        verbose_name = "fpga监控数据"
        verbose_name_plural = verbose_name