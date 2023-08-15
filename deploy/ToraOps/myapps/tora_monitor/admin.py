from django.contrib import admin
from myapps.tora_monitor import models as mmodels 
from myapps.tora_monitor import views as mviews
import myapps.tora_monitor.monitor_task as mtask


# Register your models here.

class MonitorJobAdmin(admin.ModelAdmin):
    #'month', 'day', 'hour', 'minute', 'week','day_of_week',
    list_display = ('id', 'job_id', 'job_func', 'trigger', 'is_active','last_status', 'last_runtime', 'monitor_data')

    actions = ['resume_job', 'pause_job', 'run_job']

    # 添加admin动作
    def resume_job(self, request, queryset):
        print("request: ", request)
        # for obj in queryset:
        #     print("type(obj)",type(obj))
        #     print("call resume_job")
        #     res = mviews.process_monitorJob('resume', obj)
        #     print("adminCall_res:", res)
        #     obj.is_active='1'
        #     obj.save()
            
        #queryset.update(is_active='1')
        
        
    # 指定后台界面动作的关键词
    resume_job.short_description = "激活监控项"

    # 添加admin动作
    def pause_job(self, request, queryset):
        print("request: ", request)
        # for obj in queryset:
        #     print("type(obj): ",type(obj))
        #     print("call pause_job")
        #     res = mviews.process_monitorJob('pause', obj)
        #     print("adminCall_res:", res)
        #     obj.is_active='0'
        #     obj.save()
        #queryset.update(is_active='0')
        

    # 指定后台界面动作的关键词
    pause_job.short_description = "暂停监控项"

    # 添加admin动作
    def run_job(self, request, queryset):
        print("request: ", request)
        for obj in queryset:
            print("type(obj): ",type(obj))
            print("call run_job")
            job_args = obj.job_args
            func_str = 'mtask.' + obj.job_func
            print('func_str:', func_str)
            #call_func = eval(func_str)
            if job_args :
                args_str = job_args + ';' + obj.job_id
                args = tuple(args_str.split(';'))
            else:
                args = obj.job_id
            print("argsadmin:", args, len(args))
            res = (eval(func_str))(args)
            print("adminCallrun_res:", res)

        #queryset.update(is_active='0')
        

    # 指定后台界面动作的关键词
    run_job.short_description = "立刻执行选中的监控任务"

admin.site.register(mmodels.MonitorJob, MonitorJobAdmin)

class DiskMonitorDataAdmin(admin.ModelAdmin):
    list_display = ('inner_ip', 'file_dir', 'total_size', 'usage', 'is_warning', 'is_handled', 'update_time')
admin.site.register(mmodels.DiskMonitorData, DiskMonitorDataAdmin)

class MemMonitorDataAdmin(admin.ModelAdmin):
    list_display = ('inner_ip', 'total_mem', 'usage', 'is_warning', 'is_handled', 'update_time')
admin.site.register(mmodels.MemMonitorData, MemMonitorDataAdmin)

class NodeTradeInfoAdmin(admin.ModelAdmin):
    list_display = ('engine_room','business','node_no','cur_status','online_cust_count','order_count','cancel_count','trade_count','turnover','update_time')
admin.site.register(mmodels.NodeTradeInfo, NodeTradeInfoAdmin)

class SmsControlDataAdmin(admin.ModelAdmin):
    list_display = ('init_day', 'total_used_count', 'single_limit', 'total_limit', 'update_time')
admin.site.register(mmodels.SmsControlData, SmsControlDataAdmin)

class SmsRecordDataAdmin(admin.ModelAdmin):
    list_display = ('sms_type', 'send_phones', 'create_time')
admin.site.register(mmodels.SmsRecordData, SmsRecordDataAdmin)

class ToraDatabaseMonitorCfgAdmin(admin.ModelAdmin):
    list_display = ('business','node_no','cur_status','update_time')
admin.site.register(mmodels.ToraDatabaseMonitorCfg, ToraDatabaseMonitorCfgAdmin)





# '''
# ipmi监控ip
# '''
# class ipmiMonitorIpAdmin(admin.ModelAdmin):
#     list_display = ('ipmi_ip','monitor_flag','ignore_flag')
# admin.site.register(mmodels.ipmimonitorip, ipmiMonitorIpAdmin)

'''
ipmi监控信息详情
'''
class ipmiInfoDataAdmin(admin.ModelAdmin):
    #'month', 'day', 'hour', 'minute', 'week','day_of_week',
    list_display = ('check_time','ipmi_ip', 'baseline_flag','cpu1_temp', 'cpu2_temp', 'cpu3_temp', 'cpu4_temp',
    'fan1_sp', 'fan2_sp', 'fan3_sp','fan4_sp', 'fan5_sp', 'fan6_sp','fan7_sp', 'fan8_sp', 
    'fan9_sp', 'fan10_sp', 'fan11_sp','fan12_sp', 'fan13_sp', 'fan14_sp','fan15_sp', 'fan16_sp')
    list_display_links = ('ipmi_ip',)
    search_fields = ('ipmi_ip', 'check_time', 'baseline_flag' )
    list_editable = ('baseline_flag',)
    list_per_page = 10
    ordering = ('-check_time',)

    actions = ['sortbycputemp',]
    def sortbycputemp(self, request, queryset):
        all_data=[]
        def getTemp(temp):
            if temp != '0' and temp !='' and temp !='null' and temp !=None: 
                tempList=temp.split('|')
                return int(tempList[1])
            else:
                return 0 
        for obj in queryset:
            cpu1_temp = getTemp(obj.cpu1_temp)
            cpu2_temp = getTemp(obj.cpu2_temp)
            cpu3_temp = getTemp(obj.cpu3_temp)
            cpu4_temp = getTemp(obj.cpu4_temp)
            cputemplist=[cpu1_temp,cpu2_temp,cpu3_temp,cpu4_temp]
            cputemplist.sort(reverse=True)
            cputemplist.append(obj.ipmi_ip)
            print(cputemplist)
            pass
        pass
    sortbycputemp.short_description = "按CPU温度排序"
admin.site.register(mmodels.ipmiInfoData, ipmiInfoDataAdmin)

class FpgaMonitorDataAdmin(admin.ModelAdmin):
    list_display = ('id','inner_ip','para_name','para_value','lower_limit','upper_limit','create_time')
admin.site.register(mmodels.FpgaMonitorData, FpgaMonitorDataAdmin)
