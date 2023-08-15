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
