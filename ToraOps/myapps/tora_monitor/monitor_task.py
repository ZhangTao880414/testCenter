from django.conf import settings
import os
import sys
import json
from functools import wraps
import datetime as dt
from myapps.toraapp import models as tmodels
from myapps.tora_monitor import models as mmodels
import common.common_tools as ct
import common.tora_django_common as tdc
import tora_monitor.job_scripts.ping_monitor_multhread as pmm
import tora_monitor.job_scripts.vpn_data_syn as vds
import common.server_manager_by_key as smbk
import logging
logger = logging.getLogger('django')

# Create your tests here.
#所有可以用的任务函数要在这个文件声明之后才可用。
#调用task的时候一定要传job_id,每个task返回数据格式必须{'result': '', 'data':''}

class run_monitorJob(object):
    def __init__(self, logfile='./monitor.log'):
        self.logfile = logfile
 
    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            logger.info(log_string)
            print("args11111:",args, len(args),type(args[-1]))
            if type(args[-1]) == tuple:
                job_id = args[-1][-1]
                tem_list = list(args[-1])
                tem_list.pop()
                args2 = tuple(tem_list)
            else:
                job_id = args[-1]
                tem_list = list(args)
                tem_list.pop()
                args2 = tuple(tem_list)
            print("job_id11111:", job_id)
            print("args2:", args2)
            res = func(*args2, **kwargs)
            print("res_call:", res)
            #res = {'result': True, 'data':"[{'disk_size:':100, 'memory':2400, 'msg':'ok'}]"}
            msg = "monitor_job: [%s] 执行监控项:[%s]，返回结果：[%s]" % (job_id, func.__name__, res['data'])
            if res['result']:
                logger.info("Ok,执行成功 " + msg)
            else:
                err_msg = "Error,执行失败 " + msg
                logger.error(err_msg)
                #ct.send_sms_control(err_msg)
            # # 打开logfile并写入
            # with open(self.logfile, 'a') as opened_file:
            #     # 现在将日志打到指定的文件
            #     opened_file.write(log_string + '\n')

            # 将运行结果写入MonitorJob表
            ntime = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("job_id,ntime:",job_id)
            ObjectJob = mmodels.MonitorJob.objects.filter(job_id=job_id).first()
            ObjectJob.last_runtime = ntime
            ObjectJob.last_status = res['result']
            msg = str(res['data'])
            ObjectJob.monitor_data = res['data']
            ObjectJob.save()

        return wrapped_function


def get_montior_machines():
    #machines = tmodels.ShelfMachine.objects.filter(is_active='0').first()
    machines = tmodels.ShelfMachine.objects.filter(is_active='1',is_monitor='1')
    # print(machine, type(machine))
    # print(machine.inner_ip)
    return machines

@run_monitorJob()
def test_job():
    print("I am testjob1",)
    res = {'result': True, 'data':"[{'disk_size:':100, 'memory':2400, 'msg':'ok'}]"}
    return res


@run_monitorJob()
def test_job2(para1, para2):
    print("我是apscheduler任务", para1, para2)
    res = {'result': False, 'data':"[{'disk_size:':200, 'memory':2400, 'msg':'Error'}]"}
    return res

@run_monitorJob()
def ping_shelfServer(para1):
    varify_dict = json.loads(para1)
    print("verrify:", type(varify_dict), varify_dict)
    return_data = {'result': '', 'data':''}
    res = pmm.ping_monitor_task(varify_dict)
    if res == -1:
        msg = '执行任务失败！'
        return_data['result'] = False
        return_data['data'] = msg
    elif len(res) == 0:
        return_data['result'] = True
        return_data['data'] = 'ok'
    else :
        return_data['result'] = False
        return_data['data'] = str(res)
    
    return return_data



@run_monitorJob()
def vpn_syn():
    return_data = {'result': '', 'data':''}
    res = vds.vpn_data_syn_task()
    print("async_run_res:", res, type(res))
    if res == -1:
        msg = '执行任务失败！'
        return_data['result'] = False
        return_data['data'] = msg
    elif res == 1:
        return_data['result'] = True
        return_data['data'] = 'ok'
    else :
        return_data['result'] = False
        return_data['data'] = str(res)
    
    return return_data

#对常规客户机器的硬盘占用率和内存占用率按照阀值报警
@run_monitorJob()
def cust_normal_monitor(disk_threshold=85, mem_threshold=85):
    return_data = {'result': '', 'data':''}
    machines = tmodels.ShelfMachine.objects.filter(is_active='1',is_monitor='1')
    #ip_list = ['192.168.10.214']
    disk_error_list = []
    mem_error_list = []
    try:
        for machine in machines:
            #只监控客户独用或共用的机器，奇点的另外任务
            if machine.purpose not in ['1','2']:
                continue
            hostip = machine.inner_ip
            disk_res = smbk.get_disk_info(hostip, int(disk_threshold))
            print("disk_res:",disk_res)
            if disk_res[hostip] != []:
                disk_error = {}
                ip_file_list = []
                item_dict = {}
                for item in disk_res[hostip]:
                    #print("print(len(item)):", len(item))
                #Use_Rate = int(disklist[4].split('%')[0])
                #logger.info("Use_Rate:" + disklist[4])
                    if len(item) == 6:
                        item_dict['FileSystem'] = item[0]
                        item_dict['Size'] = item[1]
                        #item_dict['Used'] = item[2]
                        #item_dict['Avail'] = item[3]
                        item_dict['Use'] = item[4]
                        #item_dict['MountedOn'] = item[5]
                        msg = "服务器：%s, 文件系统: %s 的容量：%s, 已用：%s 告警！" % (hostip,item_dict['FileSystem'],item_dict['Size'],item_dict['Use'])
                        cust_phone = tdc.get_cust_phone(hostip)
                        opm_phone = tdc.get_opm_phone()
                        print("cust_phone:", cust_phone)
                        if cust_phone != None:
                            send_phone = cust_phone + ',' + opm_phone
                            #print("send_phone:", send_phone)
                            logger.error(msg)
                            ct.send_sms_control('NoLimit', msg, send_phone)
                            #ct.send_sms_control('NoLimit', msg, '13681919346')
                        else:
                            msg2 = '客户没有手机号_' + msg
                            logger.error(msg2)
                            ct.send_sms_control('NoLimit', msg2, opm_phone)
                        ip_file_list.append(item_dict)
                    else:
                        logger.error("item 格式不对，没法处理！")
                disk_error[hostip] = ip_file_list
                disk_error_list.append(disk_error)
            else:
                logger.debug("没有需要磁盘报警的记录！")
            
            #内存监控
            mem_info = smbk.get_mem_info(hostip)
            print("mem_info:", mem_info)
            #计算b/cRate，RateMem
            BuffersCachedRate = round(100 * (int(mem_info[hostip]['Buffers']) + int(mem_info[hostip]['Cached'])) / float(mem_info[hostip]['MemTotal']), 2)
            logger.info("BuffersCachedRate:" + str("%.2f" % BuffersCachedRate) + "%")
            Free_Mem = int(mem_info[hostip]['MemFree']) + int(mem_info[hostip]['Buffers']) + int(mem_info[hostip]['Cached'])
            Used_Mem = int(mem_info[hostip]['MemTotal']) - Free_Mem
            Rate_Mem = round(100 * Used_Mem / float(mem_info[hostip]['MemTotal']),2)
            print("Rate_Mem:", Rate_Mem)
            if Rate_Mem > int(mem_threshold):
                msg = "服务器: %s 的内存使用率为：%s %%告警！" % (hostip, str(Rate_Mem))
                cust_phone = tdc.get_cust_phone(hostip)
                if cust_phone != None:
                    send_phone = cust_phone + ',13681919346'
                    ct.send_sms_control('NoLimit', msg, send_phone)
                else:
                    msg2 = '客户没有手机号_' + msg
                    ct.send_sms_control('NoLimit', msg2, '13681919346')
                #ct.send_sms_control('NoLimit', msg, '13681919346')
                mem_error_list.append({hostip: Rate_Mem})

        if len(mem_error_list) == 0 and len(disk_error_list) == 0:
            res = 1
        else:
            res = {'disk': disk_error_list, 'mem': mem_error_list}
        if res == -1:
            msg = '执行任务失败！'
            return_data['result'] = False
            return_data['data'] = msg
        elif res == 1:
            return_data['result'] = True
            return_data['data'] = "所有监控服务器的磁盘使用率没有超过 %d %%, 内存使用率没有超过 %d %%." % (int(disk_threshold), int(mem_threshold))
        else :
            return_data['result'] = False
            return_data['data'] = str(res)

    except Exception as e:
        logger.error("执行任务发生异常！",exc_info=True)
        return_data['result'] = False
        return_data['data'] = '执行任务发生异常！'

    print("return_datammmm:", return_data)
    return return_data


@run_monitorJob()
def one_time_task():
    return_data = {'result': False, 'data':''}
    res = tdc.import_cust_machine()
    print("执行完成import")
    return {'result': True, 'data':'执行任务成功！请稍后查询结果。'}
    # print("async_run_res:", res, type(res))
    # if res == -1:
    #     msg = '执行任务失败！'
    #     return_data['result'] = False
    #     return_data['data'] = msg
    # elif res == 1:
    #     return_data['result'] = True
    #     return_data['data'] = 'ok'
    # else :
    #     return_data['result'] = False
    #     return_data['data'] = str(res)
    
    # return return_data