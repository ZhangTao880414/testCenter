from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import common.tora_django_common as tdc
from multiselectfield import MultiSelectField
#import django.utils.timezone as timezone

# Create your models here.


# BUSINESS_CHOICES = (
#     ('hxzq', u'现货股票'),
#     ('sp', u'期权'),
#     ('rzrq', u'两融'),
#     ('qh', u'期货'),
# )

# APPS_CHOICES = (
#     ('tradeserver1', u'主交易'),
#     ('tradeserver2', u'备交易'),
#     ('node_md_L1', u'节点沪深L1行情'),
#     ('trade_front1', u'交易前置1'),
#     ('trade_front2', u'交易前置2'),
#     ('trade_front3', u'交易前置3'),
#     ('mq_front1', u'行情前置1'),
#     ('mq_front2', u'行情前置2'),
#     ('mq_front3', u'行情前置3'),
#     ('fens1', u'fens1'),
#     ('fens2', u'fens2'),
#     ('fens3', u'fens3'),
# )

# TASK_CHOICES = (
#     ('1', u'设备上架'),
#     ('2', u'设备下架'),
#     ('3', u'更改操作系统'),
#     ('4', u'服务器维修'),
#     ('5', u'服务器移位'),
#     ('6', u'共享资源回收'),
#     ('9', u'其他'),
# )

# TASK_STATUS = (
#     ('0', u'待处理'),
#     ('1', u'完成'),
#     ('2', u'挂起'),
#     ('9', u'失败'),
# )

# ASSERT_CHOICES = (
#     ('1', u'实体服务器'),
#     ('2', u'虚拟机'),
#     ('3', u'云服务器'),
#     ('4', u'交换机'),
#     ('9', u'不确定'),
# )

# MQ_TYPE = (
#     ('md_L2', u'沪深行情L2'),
#     ('md_L1', u'沪深行情L1'),
#     ('sse_md_L2', u'沪市行情L2'),
#     ('szse_md_L2A', u'深市行情L2'),
#     ('szse_md_L2B', u'深市行情L2_FPGA'),
#     ('qh_L1', u'期货行情L1'),
# )

# TELE_CHOICES = (
#     ('tcp', u'tcp连接'),
#     ('udp', u'upd组播'),
# )

# ROOM_CHOICES = (
#         ('shwp', u'上海宛平'),
#         ('shnq', u'上海宁桥'),
#         ('shgq', u'上海外高桥'),
#         ('shjq', u'上海金桥'),
#         ('shkj', u'上海科技网'),
#         ('shxtl', u'上海斜土路'),
#         ('dgnf', u'东莞南方'),
# )

# OWNER_CHOICES = (
#     ('1', u'客户自购'),
#     ('2', u'华鑫采购'),
#     ('3', u'Nsight自组机'),
#     ('9', u'不确定'),
# )

# PURPOSE_CHOICES = (
#     ('1', u'客户独用'),
#     ('2', u'奇点自用'),
#     ('3', u'客户共用'),
#     ('9', u'不确定'),
# )

# ASSIGN_CHOICES = (
#     ('0', u'未分配'),
#     ('1', u'已使用'),
#     ('2', u'待回收'),
#     ('3', u'已回收'),
# )

# ACTIVE_CHOICES = (
#     ('0', u'不可用'),
#     ('1', u'正常'),
#     ('4', u'维修'),
#     ('8', u'已下架'),
# )

# BOOLEAN_CHOICES = (
#     ('0', u'否'),
#     ('1', u'是'),
# )

# ACCESS_CHOICES = (
#     ('0', u'无'),
#     ('1', u'新增'),
#     ('2', u'移除'),
# )


# UPGRADE_STATUS = (
#     ('0', u'待执行'),
#     ('1', u'执行完成'),
#     ('2', u'升级中'),
#     ('3', u'回退中'),
#     ('4', u'执行失败'),
#     ('9', u'其他'),
# )

# UPGRADE_COMP = (
#     ('tradeserver1', u'主交易'),
#     ('tradeserver2', u'备交易'),
#     ('node_md_L1', u'节点沪深L1行情'),
#     ('trade_front1', u'交易前置1'),
#     ('trade_front2', u'交易前置2'),
#     ('trade_front3', u'交易前置3'),
#     ('mq_front1', u'行情前置1'),
#     ('mq_front2', u'行情前置2'),
#     ('mq_front3', u'行情前置3'),
#     ('fens1', u'fens1'),
#     ('fens2', u'fens2'),
#     ('fens3', u'fens3'),
# )

# COM_STATUS = (
#     ('0', u'异常'),
#     ('1', u'正常'),
#     ('2', u'升级中'),
#     ('3', u'回退中'),
#     ('4', u'其他'),
# )

# REQ_CHOICES = (
#     ('1', u'资源申请'),
#     ('2', u'查询'),
#     ('3', u'单独网络申请'),
#     ('5', u'客户申请回收'),
#     ('7', u'操作员强制回收'),
# )

# REQ_STATUS_CHOICES = (
#     ('0', u'待处理'),
#     ('1', u'已完成'),
#     ('4', u'已拒绝'),
#     ('9', u'处理失败'),
# )   


Choices = tdc.get_choices()
APPLY_SOURCE = tdc.dict2tuple(Choices['toraapp']['APPLY_SOURCE'])
BUSINESS_CHOICES = tdc.dict2tuple(Choices['toraapp']['BUSINESS_CHOICES'])
APPS_CHOICES = tdc.dict2tuple(Choices['toraapp']['APPS_CHOICES'])
TASK_CHOICES = tdc.dict2tuple(Choices['toraapp']['TASK_CHOICES'])
TASK_STATUS = tdc.dict2tuple(Choices['toraapp']['TASK_STATUS'])
ASSERT_CHOICES = tdc.dict2tuple(Choices['toraapp']['ASSERT_CHOICES'])
MQ_TYPE = tdc.dict2tuple(Choices['toraapp']['MQ_TYPE'])
TELE_CHOICES = tdc.dict2tuple(Choices['toraapp']['TELE_CHOICES'])
ROOM_CHOICES = tdc.dict2tuple(Choices['toraapp']['ROOM_CHOICES'])
OWNER_CHOICES = tdc.dict2tuple(Choices['toraapp']['OWNER_CHOICES'])
PURPOSE_CHOICES = tdc.dict2tuple(Choices['toraapp']['PURPOSE_CHOICES'])
ASSIGN_CHOICES = tdc.dict2tuple(Choices['toraapp']['ASSIGN_CHOICES'])
ACTIVE_CHOICES = tdc.dict2tuple(Choices['toraapp']['ACTIVE_CHOICES'])
BOOLEAN_CHOICES = tdc.dict2tuple(Choices['toraapp']['BOOLEAN_CHOICES'])
ACCESS_CHOICES = tdc.dict2tuple(Choices['toraapp']['ACCESS_CHOICES'])
UPGRADE_STATUS = tdc.dict2tuple(Choices['toraapp']['UPGRADE_STATUS'])
UPGRADE_COMP = tdc.dict2tuple(Choices['toraapp']['UPGRADE_COMP'])
COM_STATUS = tdc.dict2tuple(Choices['toraapp']['COM_STATUS'])
BEHAVIOUR_CHOICES = tdc.dict2tuple(Choices['toraapp']['BEHAVIOUR_CHOICES'])
DIRECTION_CHOICES = tdc.dict2tuple(Choices['toraapp']['DIRECTION_CHOICES'])
STATUS_CHOICES = tdc.dict2tuple(Choices['tora_monitor']['STATUS_CHOICES'])
REGISTER_CHOICES = tdc.dict2tuple(Choices['toraapp']['REGISTER_CHOICES'])



class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name='操作员', on_delete=models.CASCADE, related_name='userprofile', primary_key=True)
    role = models.CharField(verbose_name='角色', max_length=20, blank=True)
    phone = models.CharField(verbose_name='手机', unique=True, max_length=40, blank=True)
    # 用于用户头像
    avatar = models.ImageField(verbose_name='头像', upload_to='avatar/%Y%m%d/', blank=True, null=True)
    wechat = models.CharField(verbose_name='微信号', max_length=40, blank=True, null=True)

    def __str__(self):
        return self.user.__str__()

    class Meta:
        verbose_name = "操作员信息"
        verbose_name_plural = verbose_name


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
 
post_save.connect(create_user_profile, sender=User)


class ToraCustomer(models.Model):
    custgroup_name = models.CharField(verbose_name='客户组名', max_length=100, blank=True, null=True, default='custgroup_name')
    customer_NOs = models.CharField(verbose_name='客户号', max_length=200, blank=True, null=True)
    #nsight_user = models.CharField(verbose_name='NSight客户信息', max_length=20, blank=True, null=True)
    company_name = models.CharField(verbose_name='公司名称', max_length=100, blank=True, null=True)
    address = models.CharField(verbose_name='地址', max_length=200, blank=True, null=True)
    vpn_user_name = models.CharField(verbose_name='vpn用户名', max_length=254, blank=True, null=True)
    phone = models.CharField(verbose_name='手机号', max_length=254)
    email = models.EmailField(verbose_name='邮箱')
    # STATUS_CHOICES = (
    #     (u'0', u'未激活'),
    #     (u'1', u'正常'),
    # )
    status = models.CharField(verbose_name='状态', max_length=2, choices=STATUS_CHOICES, default='1')
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='操作员', related_name='customer_oper', on_delete=models.CASCADE)

    def __str__(self):
        return self.custgroup_name

    class Meta:
        verbose_name = "05-奇点客户"
        verbose_name_plural = verbose_name
        #unique_together = (('custgroup_name'),)
        ordering = ['-id']

#上架服务器信息
class ShelfMachine(models.Model): 
    engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    room_no = models.CharField(verbose_name='房间号', max_length=50, blank=True, null=True)
    row_no = models.CharField(verbose_name='排编号', max_length=50, blank=True, null=True)
    cabinet = models.CharField(verbose_name='机柜', max_length=20)
    unit = models.CharField(verbose_name='U位', max_length=10)
    #ownership = models.CharField(verbose_name='物主身份', max_length=2, choices=OWNER_CHOICES, default='9')
    owner = models.ForeignKey('ToraCustomer', verbose_name='拥有者', related_name='owner_cust', null=True, on_delete=models.SET_NULL)
    customer = models.ManyToManyField('ToraCustomer', verbose_name='使用者', related_name='use_cust', blank=True)
    purpose = models.CharField(verbose_name='使用方式', max_length=2, choices=PURPOSE_CHOICES, default='1')
    assert_type = models.CharField(verbose_name='资产类型', max_length=2, choices=ASSERT_CHOICES, default='1')
    server_brand = models.CharField(verbose_name='服务器品牌', max_length=20)
    server_model = models.CharField(verbose_name='服务器型号', max_length=50)
    producticon_date = models.DateField(verbose_name='出厂日期', max_length=50, blank=True, null=True)
    serial_number = models.CharField(verbose_name='服务器序列号', max_length=50)
    IT_checked_number = models.CharField(verbose_name='IT验收编码', max_length=20)
    assert_number = models.CharField(verbose_name='资产编码', max_length=20, blank=True, null=True)
    disk_size = models.IntegerField(verbose_name='硬盘大小G', blank=True, null=True)
    disk_type = models.CharField(verbose_name='硬盘类型', max_length=20, blank=True, null=True)
    disk_serial = models.CharField(verbose_name='硬盘序列号', max_length=50, blank=True, null=True)
    cpu_model = models.CharField(verbose_name='cpu型号', max_length=50, blank=True, null=True)
    cpu_cores = models.CharField(verbose_name='cpu核数', max_length=10, blank=True, null=True)
    memory = models.CharField(verbose_name='内存', max_length=20, blank=True, null=True)
    os = models.CharField(verbose_name='操作系统',  max_length=40, blank=True, null=True)
    os_version = models.CharField(verbose_name='系统版本', max_length=40, blank=True, null=True)
    #node_id = models.CharField(verbose_name='节点编号', max_length=4)
    node = models.ForeignKey('NodeInfo', verbose_name='节点编号', related_name='machine_node', on_delete=models.DO_NOTHING, blank=True, null=True)
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP')
    outer_ip = models.GenericIPAddressField(verbose_name='互联网IP', blank=True, null=True)
    high_trade_ip = models.GenericIPAddressField(verbose_name='高速交易IP', blank=True, null=True)
    high_mqA_ip = models.GenericIPAddressField(verbose_name='高速行情A_IP', blank=True, null=True)
    high_mqB_ip = models.GenericIPAddressField(verbose_name='高速行情B_IP', blank=True, null=True)
    ipmi_ip = models.GenericIPAddressField(verbose_name='管理口IP', blank=True, null=True)
    other_ip = models.CharField(verbose_name='其他IP', max_length=120, blank=True, null=True)
    is_active = models.CharField(verbose_name='是否可用', max_length=2, choices=ACTIVE_CHOICES, default='1') 
    is_monitor = models.CharField(verbose_name='是否监控', max_length=2, choices=BOOLEAN_CHOICES, default='0')
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    rsa_users = models.CharField(verbose_name='免密账号', max_length=254, blank=True, null=True)
    shelf_date = models.DateField(verbose_name='上架时间', blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='操作员', related_name='machine_oper', on_delete=models.CASCADE)
    #tora_service = models.ManyToManyField('ToraService', related_name='server_tora', blank=True, null=True)
    
    def __str__(self):
        return self.inner_ip
    
    class Meta:
        verbose_name = "11-已上架服务器"
        verbose_name_plural = verbose_name
        #unique_together = (('serial_number'),)
        ordering = ['-id']


class TaskFlow(models.Model): 	
    apply_source = models.CharField(verbose_name='发起来源', max_length=2, choices=APPLY_SOURCE, default='0')
    task_type = models.CharField(verbose_name='任务类型', max_length=2, choices=TASK_CHOICES)
    #customer = models.ManyToManyField('ToraCustomer', verbose_name='使用客户', related_name='task_cust', blank=True)
    customer = models.ForeignKey('ToraCustomer', verbose_name='使用客户', related_name='task_cust', blank=True, null=True, on_delete=models.CASCADE)
    #custgroup_name前端不需要展示
    custgroup_name = models.CharField(verbose_name='客户组名', max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True,verbose_name='邮箱')
    engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    ownership = models.CharField(verbose_name='物主身份', max_length=2, choices=OWNER_CHOICES, default='9')
    purpose = models.CharField(verbose_name='使用方式', max_length=2, choices=PURPOSE_CHOICES, default='9')
    #上架完成时必填
    #vpn传入客户已有vpn账号，没有的话前台传值为None
    is_new_vpn = models.CharField(verbose_name='是否新分配vpn(格式：1;0;1最多设置5个)', max_length=10)
    vpn_user_name = models.CharField(verbose_name='vpn用户名', max_length=254)
    vpn_phone = models.CharField(verbose_name='vpn注册手机号', max_length=254, blank=True, null=True)
    sys_user_name = models.CharField(verbose_name='系统用户名', max_length=20, blank=True, null=True)
    sys_user_passwd = models.CharField(verbose_name='系统密码', max_length=40, blank=True, null=True)
    access_action = models.CharField(verbose_name='网络授权', max_length=2, choices=ACCESS_CHOICES, default='0')
    access_address = models.CharField(verbose_name='授权外网地址端口', max_length=200, blank=True, null=True)
    access_finished = models.CharField(verbose_name='网络授权完成状态', max_length=2, choices=BOOLEAN_CHOICES, default='0')
    room_no = models.DateField(verbose_name='房间号', max_length=50, blank=True, null=True)
    row_no = models.DateField(verbose_name='排编号', max_length=50, blank=True, null=True)
    cabinet = models.CharField(verbose_name='机柜', max_length=20, blank=True, null=True)
    unit = models.CharField(verbose_name='U位', max_length=10, blank=True, null=True)
    assert_type = models.CharField(verbose_name='资产类型', max_length=2, choices=ASSERT_CHOICES, default='1')
    server_brand = models.CharField(verbose_name='服务器品牌', max_length=20, blank=True, null=True)
    server_model = models.CharField(verbose_name='服务器型号', max_length=50, blank=True, null=True)
    producticon_date = models.DateField(verbose_name='出厂日期', max_length=50, blank=True, null=True)
    #下架时必填
    serial_number = models.CharField(verbose_name='服务器序列号', max_length=50, blank=True, null=True)
    IT_checked_number = models.CharField(verbose_name='IT验收编码', max_length=20, blank=True, null=True)
    #node_id = models.CharField(verbose_name='节点编号', max_length=4)
    node = models.ForeignKey('NodeInfo', verbose_name='节点编号', related_name='task_node', on_delete=models.CASCADE)
    os = models.CharField(verbose_name='操作系统', max_length=40, blank=True, null=True)
    os_version = models.CharField(verbose_name='系统版本', max_length=40, blank=True, null=True)
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP', blank=True, null=True)
    outer_ip = models.GenericIPAddressField(verbose_name='互联网IP', blank=True, null=True)
    high_trade_ip = models.GenericIPAddressField(verbose_name='高速交易IP', blank=True, null=True)
    high_mqA_ip = models.GenericIPAddressField(verbose_name='高速行情A_IP', blank=True, null=True)
    high_mqB_ip = models.GenericIPAddressField(verbose_name='高速行情B_IP', blank=True, null=True)
    ipmi_ip = models.GenericIPAddressField(verbose_name='管理口IP', blank=True, null=True)
    other_ip = models.CharField(verbose_name='其他IP', max_length=120, blank=True, null=True)
    task_status = models.CharField(verbose_name='任务状态', max_length=2, choices=TASK_STATUS, default='0') 
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    other_msg = models.TextField(verbose_name='客户模板信息', blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='创建者', related_name='taskadd_user', blank=True, on_delete=models.CASCADE)
    modify_oper = models.ForeignKey('auth.User', verbose_name='修改者', related_name='taskmodify_user', blank=True, null=True, on_delete=models.CASCADE)
 
    def __str__(self):
        #print("self.customer:", self.customer, self.customer_id)
        return str(self.custgroup_name)
    class Meta:
        verbose_name = "10-运维任务流水"
        verbose_name_plural = verbose_name
        ordering = ['-id']


class ToraService(models.Model):
    #node_id = models.CharField(verbose_name='节点编号', max_length=4)
    node = models.ForeignKey('NodeInfo', verbose_name='节点编号', related_name='service_node', on_delete=models.CASCADE)
    business = models.CharField(verbose_name='业务', max_length=20, choices=BUSINESS_CHOICES)
    processes = models.CharField(verbose_name='进程', max_length=254, blank=True, null=True)
    ports = models.CharField(verbose_name='端口', max_length=254, blank=True, null=True)
    sse_trade_ip = models.GenericIPAddressField(verbose_name='SSE交易ip', blank=True, null=True)
    sse_dx_L2_ip = models.GenericIPAddressField(verbose_name='SSE电信L2行情', blank=True, null=True)
    sse_lt_L2_ip = models.GenericIPAddressField(verbose_name='SSE联通L2行情', blank=True, null=True)
    szse_trade1_ip = models.GenericIPAddressField(verbose_name='SZSE交易1', blank=True, null=True)
    szse_trade2_ip = models.GenericIPAddressField(verbose_name='SZSE交易2', blank=True, null=True)
    szse_L2_ip = models.GenericIPAddressField(verbose_name='SZSEL2行情网段', blank=True, null=True)
    sse_nq_mq_A = models.GenericIPAddressField(verbose_name='宁桥SSE行情A路地址', blank=True, null=True)
    sse_nq_mq_B = models.GenericIPAddressField(verbose_name='宁桥SSE行情B路地址', blank=True, null=True)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    machine = models.OneToOneField("ShelfMachine", verbose_name='服务器信息', on_delete=models.SET_NULL, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return str(self.machine)

    class Meta:
        verbose_name = "奇点服务器进程和端口"
        verbose_name_plural = verbose_name
        ordering = ['-id']


class NodeInfo(models.Model):
    node_no = models.CharField(verbose_name='节点编号', max_length=4, unique=True)
    node_name = models.CharField(verbose_name="节点名称", max_length=20, unique=True)
    business = MultiSelectField(verbose_name='业务', choices=BUSINESS_CHOICES, blank=True, null=True)
    engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    #mq = models.ForeignKey('ToraMqGroup', verbose_name='对应行情组', related_name='node_mq', on_delete=models.CASCADE, blank=True, null=True)
    node_cfg_module = models.TextField(verbose_name='客户邮件模板信息', blank=True, null=True)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    
    def __str__(self):
        return self.node_no

    class Meta:
        verbose_name = "01-节点信息"
        verbose_name_plural = verbose_name
        ordering = ['-id']
        #unique_together = (('node_id'),)


class NodeDetailInfo(models.Model):
    node = models.ForeignKey('NodeInfo', verbose_name='节点编号', related_name='component_node', on_delete=models.CASCADE)
    business = models.CharField(verbose_name='业务', max_length=20, choices=BUSINESS_CHOICES)
    ip_addr = models.CharField(verbose_name='地址', max_length=254,  blank=True, null=True)
    component = models.CharField(verbose_name='组件', max_length=100, blank=True, null=True)
    port = models.CharField(verbose_name='端口', max_length=40, blank=True, null=True)
    current_version = models.CharField(verbose_name='当前系统版本', max_length=100, default='1.0')
    upgrade_time = models.DateTimeField(verbose_name='升级时间', blank=True, null=True)
    last_back_dir = models.CharField(verbose_name='最新备份目录', max_length=100, blank=True, null=True)
    back_time = models.DateTimeField(verbose_name='备份时间', blank=True, null=True)
    sys_status = models.CharField(verbose_name='当前状态', max_length=10, choices=COM_STATUS, blank=True, null=True)
    monitor_time = models.DateTimeField(verbose_name='监控时间', blank=True, null=True)
    operator = models.ForeignKey('auth.User', verbose_name='创建者', related_name='comp_add_user', blank=True, on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)                     

    def __str__(self):
        #return str(self.node + '_' + self.business)
        return self.current_version

    class Meta:
        verbose_name = "03-节点详细信息"
        verbose_name_plural = verbose_name
        ordering = ['-id']


class UpgradeTask(models.Model):
    node = models.ManyToManyField('NodeInfo', verbose_name='节点编号', related_name='upgrade_node')
    business = models.CharField(verbose_name='业务', max_length=20, choices=BUSINESS_CHOICES)
    #component = models.ManyToManyField('NodeComponentInfo', verbose_name='组件', related_name='upgrade_comp')
    component = MultiSelectField(verbose_name='升级组件', choices=UPGRADE_COMP, blank=True, null=True)
    # current_version = models.CharField(verbose_name='当前版本', max_length=100, blank=True, null=True)
    # upgrade_time = models.DateTimeField(verbose_name='升级时间', blank=True, null=True)
    upgrade_version = models.CharField(verbose_name='升级版本号', max_length=100)
    upgrade_dir = models.CharField(verbose_name='升级目录', max_length=100, blank=True, null=True)
    task_status = models.CharField(verbose_name='任务状态', max_length=10, choices=UPGRADE_STATUS, blank=True, null=True, default='0')
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='创建者', related_name='upgrade_user', blank=True, on_delete=models.CASCADE)

    def __str__(self):
        #return str(self.node + '_' + self.business)
        return self.upgrade_version

    class Meta:
        verbose_name = "00-升级任务"
        verbose_name_plural = verbose_name
        ordering = ['-id']



class TradeNode(models.Model):
    #engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    node = models.ForeignKey('NodeInfo', verbose_name='节点编号', related_name='trade_node', on_delete=models.CASCADE)
    business = models.CharField(verbose_name='业务', max_length=20, choices=BUSINESS_CHOICES)
    app_type = models.CharField(verbose_name='服务类型', max_length=20, choices=APPS_CHOICES)
    ip_addr = models.CharField(verbose_name='地址', max_length=40)
    port = models.CharField(verbose_name='端口', max_length=20)
    internet_addr_ports = models.CharField(verbose_name='互联网地址端口', max_length=100, blank=True, null=True)
    #internet_port = models.CharField(verbose_name='互联网端口', max_length=20, blank=True, null=True)
    # process = models.CharField(verbose_name='进程', max_length=20)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return str(self.node)

    class Meta:
        verbose_name = "02-节点交易信息"
        verbose_name_plural = verbose_name
        ordering = ['-id']


class ToraMqGroup(models.Model):
    mq_group_name = models.CharField(verbose_name='行情组名称', max_length=20)
    engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return self.mq_group_name

    class Meta:
        verbose_name = "04-行情组配置"
        verbose_name_plural = verbose_name
        ordering = ['-id']



class ToraMq(models.Model):
    #mq_group = models.ForeignKey('ToraMqGroup', verbose_name='行情组', related_name='group_mq', on_delete=models.CASCADE)
    #mq_name = models.CharField(verbose_name='行情服务名称', max_length=20)
    #engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    #node = models.ForeignKey('NodeInfo', verbose_name='节点编号', related_name='L2mq_node', on_delete=models.CASCADE)
    node_nos = models.CharField(verbose_name='覆盖的节点', max_length=50, blank=True, null=True)
    business = MultiSelectField(verbose_name='业务', choices=BUSINESS_CHOICES, blank=True, null=True)
    register_type = models.CharField(verbose_name='注册方式', max_length=20, choices=REGISTER_CHOICES,default='tcp')
    mq_type = models.CharField(verbose_name='行情类型', max_length=20, choices=MQ_TYPE)
    tele_pattern = models.CharField(verbose_name='通讯模式', max_length=10, choices=TELE_CHOICES)
    ip_addr = models.CharField(verbose_name='地址', max_length=40)
    port = models.CharField(verbose_name='端口', max_length=20)
    md_rec_addr = models.CharField(verbose_name='行情可接收地址段', max_length=40, blank=True, null=True)
    source_ip = models.CharField(verbose_name='源IP', max_length=40, blank=True, null=True)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return self.ip_addr

    class Meta:
        verbose_name = "06-行情服务信息"
        verbose_name_plural = verbose_name
        ordering = ['-id']



# #cfg/server.csv和DeployConfig.xml
# class tora_cfg_server(models.Model):
#     node_id = models.CharField(verbose_name='节点编号', max_length=4)
#     business = models.CharField(verbose_name='业务', max_length=20, choices=BUSINESS_CHOICES)
#     group = models.CharField(max_length=20)
#     server = models.CharField(max_length=20)
#     IP = models.GenericIPAddressField()
#     args = models.CharField(max_length=20)
#     port = models.CharField(max_length=20, blank=True, null=True)
#     version = models.CharField(verbose_name='服务类型', max_length=20, blank=True, null=True)
#     is_backup = models.CharField(max_length=2, default=1)
#     pre_cmd = models.CharField(max_length=40, blank=True, null=True)
#     user_pwd = models.CharField(max_length=40, blank=True, null=True)
#     comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
#     create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
#     update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
#     operator = models.ForeignKey('auth.User', verbose_name='操作员', related_name='customer_oper', on_delete=models.CASCADE)






# class OpsOperLog(models.Model):
#     log_time = models.DateTimeField()
#     function = models.CharField(max_length=20)
#     action_type = models.CharField(max_length=10)
#     action_detail = models.CharField(max_length=100, blank=True, null=True)
#     opt_object = models.CharField(max_length=20, blank=True, null=True)
#     comment = models.CharField(max_length=40, blank=True, null=True)
#     operator = models.CharField(max_length=20, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'ops_oper_log'


# class ResourceApplyInfo(models.Model):
#     req_type = models.CharField(verbose_name='请求类型', max_length=10, choices=BEHAVIOUR_CHOICES)
#     apply_id = models.CharField(verbose_name='申请ID', unique=True, max_length=14)
#     nsight_user = models.CharField(verbose_name='Nsight用户信息', max_length=20)
#     product_info = models.CharField(verbose_name='用户产品信息', max_length=20, blank=True, null=True)
#     inner_ip = models.CharField(verbose_name='内网IP', max_length=20)
#     outer_ip = models.CharField(verbose_name='外网IP', max_length=20, blank=True, null=True)
#     sys_user_name = models.CharField(verbose_name='系统用户名', max_length=20, blank=True, null=True)
#     sys_user_passwd = models.CharField(verbose_name='系统用户密码', max_length=40, blank=True, null=True)
#     vpn_address = models.CharField(verbose_name='vpn连接地址', max_length=40, blank=True, null=True)
#     vpn_user_name = models.CharField(verbose_name='vpn用户名', max_length=20, blank=True, null=True)
#     vpn_user_passwd = models.CharField(verbose_name='vpn用户密码', max_length=40, blank=True, null=True)
#     access_action = models.CharField(verbose_name='网络操作', max_length=2, choices=ACCESS_CHOICES, default='0')
#     customer_access = models.CharField(verbose_name='外网访问地址端口', max_length=200, blank=True, null=True)    
#     req_status = models.CharField(verbose_name='请求状态', max_length=2, choices=REQ_STATUS_CHOICES, default='0')
#     res_msg = models.CharField(verbose_name='返回消息', max_length=200, blank=True, null=True)
#     create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
#     update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
#     modify_oper = models.ForeignKey('auth.User', verbose_name='更新操作员', related_name='resouce_mod_oper', on_delete=models.CASCADE)

#     def __str__(self):
#         return self.nsight_user

#     class Meta:
#         verbose_name = "NSight资源申请"
#         verbose_name_plural = verbose_name
#         ordering = ['-id']


class SystemUserInfo(models.Model):
    engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP')
    sys_user_name = models.CharField(verbose_name='用户名', max_length=20)
    sys_user_passwd = models.CharField(verbose_name='密码', max_length=40, blank=True, null=True)
    cur_status = models.CharField(verbose_name='当前状态', max_length=2, choices=ASSIGN_CHOICES, default='0')
    #nsight_user = models.CharField(verbose_name='NSight客户信息', max_length=20, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='创建者', related_name='sysadd_oper', blank=True, on_delete=models.CASCADE)
    customer = models.ForeignKey('ToraCustomer', verbose_name='使用客户', related_name='sys_user_cust', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return (self.inner_ip + '_' + self.sys_user_name)

    class Meta:
        verbose_name = "13-系统账号信息"
        verbose_name_plural = verbose_name
        unique_together = (('inner_ip', 'sys_user_name'),)
        ordering = ['-id']


class VpnUserInfo(models.Model):
    engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    vpn_address = models.CharField(verbose_name='vpn连接地址', max_length=40, blank=True, null=True)
    vpn_user_name = models.CharField(verbose_name='vpn账号', max_length=20)
    vpn_phone = models.CharField(verbose_name='vpn注册手机号', max_length=40,default='')
    vpn_user_passwd = models.CharField(verbose_name='vpn密码',max_length=40, blank=True, null=True)
    cur_status = models.CharField(verbose_name='当前状态', max_length=2, choices=ASSIGN_CHOICES, default='1')
    #nsight_user = models.CharField(verbose_name='NSight客户信息', max_length=20, blank=True, null=True)
    server_list = models.TextField(verbose_name='服务器列表', blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='创建者', related_name='vpnadd_oper', blank=True, on_delete=models.CASCADE)
    customer = models.ForeignKey('ToraCustomer', verbose_name='使用客户', related_name='vpn_user_cust', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.vpn_user_name

    class Meta:
        verbose_name = '12-vpn账号信息'
        verbose_name_plural = verbose_name
        unique_together = (('vpn_address', 'vpn_user_name'),)
        ordering = ['-id']


class VpnCfgInfo(models.Model):
    engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    vpn_address = models.CharField(verbose_name='vpn连接地址', max_length=40)
    vpn_init_passwd = models.CharField(verbose_name='vpn初始密码',max_length=40)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='创建者', related_name='vpncfg_oper', blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.vpn_address

    class Meta:
        verbose_name = '81-vpn配置信息'
        verbose_name_plural = verbose_name
        ordering = ['-id']



# class CustNodeMailModul(models.Model):
#     #engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
#     node = models.ForeignKey('NodeInfo', verbose_name='节点编号', related_name='mail_node', on_delete=models.CASCADE)
#     mail_content = models.TextField(verbose_name='界面邮件模板信息', blank=True, null=True)
#     comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
#     create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
#     update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

#     def __str__(self):
#         return self.vpn_user_name

#     class Meta:
#         verbose_name = '92-客户节点邮件模板配置'
#         verbose_name_plural = verbose_name
#         ordering = ['-id']



# class share_node_info(models.Model):
#     business = models.CharField(max_length=4)
#     engine_room = models.CharField(max_length=10, blank=True, null=True)
#     node_id = models.CharField(max_length=4)
#     app_type = models.CharField(max_length=12)
#     tele_pattern = models.CharField(max_length=12)
#     ip_addr = models.CharField(max_length=40, blank=True, null=True)
#     port = models.CharField(max_length=20, blank=True, null=True)
#     md_rec_addr = models.CharField(max_length=10, blank=True, null=True)
#     comment = models.CharField(max_length=40, blank=True, null=True)
#     operator = models.CharField(max_length=20, blank=True, null=True)
#     create_time = models.DateTimeField()
#     update_time = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         #db_table = 'share_node_info'
#         unique_together = (('business', 'engine_room', 'node_id', 'app_type', 'tele_pattern'),)


# class share_servers_info(models.Model):
#     engine_room = models.CharField(max_length=10)
#     node_id = models.CharField(max_length=4)
#     server_type = models.CharField(max_length=2)
#     serial_number = models.CharField(unique=True, max_length=20)
#     os = models.CharField(max_length=12)
#     os_version = models.CharField(max_length=12)
#     cpu_model = models.CharField(max_length=50, blank=True, null=True)
#     cpu_cores = models.CharField(max_length=4, blank=True, null=True)
#     memory = models.CharField(max_length=10, blank=True, null=True)
#     disk_size = models.CharField(max_length=10, blank=True, null=True)
#     disk_type = models.CharField(max_length=10, blank=True, null=True)
#     inner_ip = models.CharField(max_length=20)
#     outer_ip = models.CharField(max_length=20)
#     high_trade_ip = models.CharField(max_length=20, blank=True, null=True)
#     high_mqa_ip = models.CharField(db_column='high_mqA_ip', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     high_mqb_ip = models.CharField(db_column='high_mqB_ip', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     ipmi_ip = models.CharField(max_length=20, blank=True, null=True)
#     is_available = models.CharField(max_length=2, blank=True, null=True)
#     assigned_count = models.IntegerField(blank=True, null=True)
#     operator = models.CharField(max_length=20, blank=True, null=True)
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)

#     class Meta:
#         # managed = False
#         verbose_name = 'share_servers_info'


class ShareServerInfo(models.Model):
    
    engine_room = models.CharField(verbose_name='机房', max_length=10, choices=ROOM_CHOICES)
    #node = models.ForeignKey('NodeInfo', verbose_name='节点编号', related_name='trade_node', on_delete=models.CASCADE)
    share_type = models.CharField(verbose_name='共享类型', max_length=2, choices=PURPOSE_CHOICES)
    machine = models.OneToOneField("ShelfMachine", verbose_name='服务器信息', on_delete=models.CASCADE)
    is_active = models.CharField(verbose_name='是否可用', max_length=2, choices=ACTIVE_CHOICES, default='1')
    assigned_count = models.IntegerField(verbose_name='已分配客户数量', blank=True, null=True, default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='创建者', related_name='shareser_add_oper', blank=True, on_delete=models.CASCADE)
    assigned_cust = models.ManyToManyField('ToraCustomer', verbose_name='已分配客户', related_name='share_server_cust', blank=True)
    vpn_list = models.TextField(verbose_name='可访问的vpn列表', blank=True, null=True)
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)

    def __str__(self):
        return str(self.machine)

    class Meta:
        verbose_name = '14-共享服务器信息'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class Area(models.Model):    
    name = models.CharField(max_length=20, verbose_name='名称')
    # 自关联(特殊的一对多): 生成的字段名 parent_id
    parent = models.ForeignKey('self', verbose_name='上级行政区划', related_name='area_pare', blank=True, null=True, on_delete=models.SET_NULL)
    area_no = models.CharField(verbose_name='区号', max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class GloblePara(models.Model):    
    para_name = models.CharField(max_length=40, verbose_name='参数名称')
    para_value = models.CharField(max_length=128, verbose_name='参数值')
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='创建者', related_name='paraadd_user', blank=True, on_delete=models.CASCADE)
    modify_oper = models.ForeignKey('auth.User', verbose_name='修改者', related_name='paramodify_user', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.para_name)

    class Meta:

        verbose_name = '全局参数设置'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class AccessApplyInfo(models.Model):
    task = models.ForeignKey('TaskFlow', verbose_name='运维流水', related_name='access_task', blank=True, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey('ToraCustomer', verbose_name='使用客户', related_name='access_cust', blank=True, on_delete=models.CASCADE)
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP', blank=True, null=True)
    outer_ip = models.GenericIPAddressField(verbose_name='互联网IP', blank=True, null=True)
    in_service_ports = models.GenericIPAddressField(verbose_name='内部端口', blank=True, null=True)
    access_action = models.CharField(verbose_name='网络授权', max_length=2, choices=ACCESS_CHOICES, default='0')
    behaviour = models.CharField(verbose_name='行为', max_length=2, blank=True, null=True, choices=BEHAVIOUR_CHOICES, default='0')
    direction = models.CharField(verbose_name='访问方向', max_length=2, blank=True, null=True, choices=DIRECTION_CHOICES, default='0')
    customer_ip = models.CharField(verbose_name='客户外网地址', max_length=200, blank=True, null=True)
    customer_ports = models.CharField(verbose_name='客户外网端口', max_length=200, blank=True, null=True)
    assigned_out_ip = models.CharField(verbose_name='映射互联网地址', max_length=200, blank=True, null=True)
    assigned_out_ports = models.CharField(verbose_name='映射互联网端口', max_length=200, blank=True, null=True)
    cur_status = models.CharField(verbose_name='当前状态', max_length=2, choices=TASK_STATUS, default='1')
    comment = models.CharField(verbose_name='备注', max_length=254, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    operator = models.ForeignKey('auth.User', verbose_name='创建者', related_name='accessadd_user', blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.inner_ip)

    class Meta:

        verbose_name = '网络访问申请记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']