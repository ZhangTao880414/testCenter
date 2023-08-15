from django.contrib import admin
from myapps.toraapp import models 
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
import common.tora_django_common as tdc
import common.server_manager_by_key as csmk
import logging
logger = logging.getLogger('django')


# Register your models here.
#admin.site.register(models.UserInfo)
admin.site.register(models.Area)
class ToraCustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'custgroup_name', 'company_name', 'email', 'status')
    search_fields = ('custgroup_name', 'company_name', 'phone', 'email')
admin.site.register(models.ToraCustomer, ToraCustomerAdmin)
class ShelfMachineAdmin(admin.ModelAdmin):
    list_display = ('id', 'node', 'engine_room','cabinet', 'unit', 'serial_number', 'IT_checked_number', 'purpose', 'inner_ip', 'owner')
    search_fields = ('serial_number', 'engine_room', 'inner_ip', 'IT_checked_number', 'purpose')
    actions = ['copy_ssh_rsa','set_local_yum','env_optimizing']

    # 添加admin动作
    def copy_ssh_rsa(self, request, queryset):
        #print("request: ", request)
        print("call copy_ssh_rsa")
        res = tdc.copy_ssh_rsa(queryset)
        #res = {'code':1, 'data':'success'}
        #res = {'code':0, 'data':['192.168.20.102']}
        if res['code'] == 1:
            self.message_user(request, '免密增加成功')
        else:
            msg = '免密增加有失败的IP: %s' % (str(res['data']))
            logger.error(msg)
            self.message_user(request, msg)
        
    # 指定后台界面动作的关键词
    copy_ssh_rsa.short_description = "服务器免密操作"

    def set_local_yum(self, request, queryset):
        #print("request: ", request)
        print("call set_local_yum")
    set_local_yum.short_description = "设置内网Yum源"

    def env_optimizing(self, request, queryset):
        #print("request: ", request)
        print("call env_optimizing")
    env_optimizing.short_description = "linux系统环境设置和优化"

admin.site.register(models.ShelfMachine, ShelfMachineAdmin)
admin.site.register(models.ToraService)
class SystemUserInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'engine_room', 'inner_ip', 'sys_user_name', 'cur_status', 'customer')
admin.site.register(models.SystemUserInfo, SystemUserInfoAdmin)
class VpnUserInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'engine_room', 'vpn_address', 'vpn_user_name', 'vpn_phone', 'cur_status', 'customer')
admin.site.register(models.VpnUserInfo, VpnUserInfoAdmin)
class VpnCfgInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'engine_room', 'vpn_address')
admin.site.register(models.VpnCfgInfo, VpnCfgInfoAdmin)

class TaskFlowAdmin(admin.ModelAdmin):
    list_display = ('id', 'apply_source', 'custgroup_name', 'task_type', 'node', 'serial_number', 'engine_room', 'inner_ip', 'task_status')
    search_fields = ('serial_number', 'engine_room', 'inner_ip', 'custgroup_name')
admin.site.register(models.TaskFlow, TaskFlowAdmin)
class NodeInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'node_no', 'node_name', 'engine_room')
    actions = ['gen_node_cfg_module']

    # 添加admin动作
    def gen_node_cfg_module(self, request, queryset):
        print("request: ", request)
        # queryset.update(task_status='2')
        # for obj in queryset:
        #     print(obj)
        print("gen_node_cfg_module")
        tdc.gen_node_cfg_module(queryset)
        self.message_user(request, '模板生产完成！')
        
    # 指定后台界面动作的关键词
    gen_node_cfg_module.short_description = "生成节点邮件模板"
admin.site.register(models.NodeInfo, NodeInfoAdmin)

class ShareServerInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'engine_room', 'share_type', 'machine', 'is_active', 'assigned_count')
    actions = ['create_sys_user']

    # 添加admin动作
    def create_sys_user(self, request, queryset):
        print("request: ", request)
        print("call create_sys_user")
        csmk.create_n_users(queryset)
        
    # 指定后台界面动作的关键词
    create_sys_user.short_description = "批量创建系统用户"
admin.site.register(models.ShareServerInfo, ShareServerInfoAdmin)
class TradeNodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'node', 'business', 'app_type', 'ip_addr', 'port')
admin.site.register(models.TradeNode, TradeNodeAdmin)
class ToraMqAdmin(admin.ModelAdmin):
    list_display = ('id', 'mq_type', 'ip_addr', 'port')
admin.site.register(models.ToraMq, ToraMqAdmin)
class ToraMqGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'mq_group_name', 'engine_room', 'comment', 'create_time')
admin.site.register(models.ToraMqGroup, ToraMqGroupAdmin)

class NodeDetailInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'node', 'business')
admin.site.register(models.NodeDetailInfo, NodeDetailInfoAdmin)


class UpgradeTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'upgrade_version', 'task_status', 'create_time', 'update_time', 'operator')
    actions = ['node_upgrade', 'node_restore']

    # 添加admin动作
    def node_upgrade(self, request, queryset):
        print("request: ", request)
        queryset.update(task_status='2')
        # for obj in queryset:
        #     print(obj)
        print("call upgrade")
        #tdc.nodeUpgrade(queryset)
        self.message_user(request, '执行升级任务中，请稍后查询任务状态')
        
    # 指定后台界面动作的关键词
    node_upgrade.short_description = "节点升级版本"

    # 添加admin动作
    def node_restore(self, request, queryset):
        queryset.update(task_status='3')
        print("call restore")
        #tdc.nodeRestore(queryset)
        self.message_user(request, '执行版本回退任务中，请稍后查询任务状态')
    # 指定后台界面动作的关键词
    node_restore.short_description = "节点版本回退"
    #call back restore
admin.site.register(models.UpgradeTask, UpgradeTaskAdmin)


class ProfileInline(admin.StackedInline):
    model = models.UserProfile
    #fk_name = 'user'
    max_num = 1
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline,]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class GlobleParaAdmin(admin.ModelAdmin):
    list_display = ('id', 'para_name', 'para_value')
admin.site.register(models.GloblePara, GlobleParaAdmin)

class AccessApplyInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'inner_ip', 'outer_ip', 'in_service_ports', 'access_action', 'direction', 'customer_ip', 'customer_ports', 'cur_status')
admin.site.register(models.AccessApplyInfo, AccessApplyInfoAdmin)