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
#import common.sms_control as smsc
import tora_monitor.job_scripts.ping_monitor_multhread as pmm
import tora_monitor.job_scripts.vpn_data_syn as vds
import tora_monitor.job_scripts.fpga_check as mfpga
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


# def send_cust_error_sms(hostip, msg):
#     cust_phone = tdc.get_cust_phone(hostip)
#     opm_phone = tdc.get_opm_phone()
#     print("cust_phone:", cust_phone)
#     if cust_phone != None:
#         send_phone = cust_phone + ',' + opm_phone
#         #print("send_phone:", send_phone)
#         logger.error(msg)
#         ct.send_sms_control('NoLimit', msg, send_phone)
#         #ct.send_sms_control('NoLimit', msg, '13681919346')
#     else:
#         msg2 = '客户没有手机号_' + msg
#         logger.error(msg2)
#         ct.send_sms_control('NoLimit', msg2, opm_phone)


def get_ras_user(inner_ip):
    machine = tmodels.ShelfMachine.objects.filter(inner_ip=inner_ip).first()
    users = machine.rsa_users
    if users:
        user_list = users.split(",")
        if 'root' in user_list:
            return 'root'
        else:
            return user_list[0]
    else:
        return None


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
    #print("call cust_nomrlmonot!!!")
    return_data = {'result': '', 'data':''}
    machines = tmodels.ShelfMachine.objects.filter(is_active='1',is_monitor='1')
    #ip_list = ['192.168.10.214']
    #print("machines:", machines)
    disk_error_list = []
    mem_error_list = []
    try:
        for machine in machines:
            #只监控客户独用或共用的机器，奇点的另外任务
            if machine.purpose not in ['1','2','4']:
                continue
            hostip = machine.inner_ip
            rsa_user = get_ras_user(hostip)
            #print("rsa_user:", rsa_user)
            disk_res = smbk.get_disk_info(rsa_user, hostip)
            print("disk_res:",disk_res)
            #需要对结果进行判断或者在调用接口时判断。
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
                        if item[1][-1] == 'M':
                            item_dict['Size'] = round(float(item[1][:-1]) / 1024, 2)
                        else :
                            item_dict['Size'] = round(float(item[1][:-1]), 2)

                        if str(item[2][-1]) == '0':
                            item_dict['Used'] = 0
                        elif item[2][-1] =='M':
                            item_dict['Used'] = round(float(item[2][:-1]) / 1024, 2)
                        else:
                            item_dict['Used'] = round(float(item[2][:-1]), 2)

                        if item[3][-1] == 'M':
                            item_dict['Avail'] = round(float(item[3][:-1]) / 1024, 2)
                        else :
                            item_dict['Avail'] = round(float(item[3][:-1]), 2)

                        item_dict['Use'] = float(item[4][:-1])
                        item_dict['MountedOn'] = item[5]

                        #判断
                        if item_dict['Use'] >= int(disk_threshold):
                            msg = "服务器：%s, 文件系统: %s 的容量：%s, 已用：%s %%告警！" % (hostip,item_dict['FileSystem'],str(item_dict['Size']),str(item_dict['Use']))
                            tdc.send_cust_error_sms(hostip, msg)
                            ip_file_list.append(item_dict)
                            #写库
                            dic = {'inner_ip': hostip,
                                'file_dir': item_dict['FileSystem'], 
                                'total_size': item_dict['Size'],
                                'used_size': item_dict['Used'],
                                'avail_size': item_dict['Avail'],
                                'usage': item_dict['Use'],   
                                'mounted_on': item_dict['MountedOn'],
                                'is_warning': '1',
                                'is_handled': '1'}                          
                            mmodels.DiskMonitorData.objects.create(**dic)
                        else:
                            #写库
                            dic = {'inner_ip': hostip,
                                'file_dir': item_dict['FileSystem'], 
                                'total_size': item_dict['Size'],
                                'used_size': item_dict['Used'],
                                'avail_size': item_dict['Avail'],
                                'usage': item_dict['Use'],   
                                'mounted_on': item_dict['MountedOn']}                          
                            mmodels.DiskMonitorData.objects.create(**dic)
                        
                    else:
                        msg = "服务器%s取disk信息，返回item 格式不对，没法处理！" % hostip
                        logger.error(msg)
                        ct.send_sms_control('NoLimit',msg,'13681919346')
                if len(ip_file_list) != 0:
                    disk_error[hostip] = ip_file_list
                    disk_error_list.append(disk_error)
            else:
                logger.debug("没有需要磁盘报警的记录！")
            
            #内存监控
            mem_info = smbk.get_mem_info(rsa_user,hostip)
            print("mem_info:", mem_info)
            #mem_info: {'10.168.8.91': {}}
            if mem_info[hostip] == {}:
                msg = "error服务器%s没有取到内存数据！" % hostip
                logger.error(msg)
                #api异常会发送报警短信
                #tdc.send_monitor_sms('NoLimit',msg,'13681919346')
            else:
                #计算b/cRate，RateMem
                BuffersCachedRate = round(100 * (int(mem_info[hostip]['Buffers']) + int(mem_info[hostip]['Cached'])) / float(mem_info[hostip]['MemTotal']), 2)
                logger.info("BuffersCachedRate:" + str("%.2f" % BuffersCachedRate) + "%")
                Free_Mem = float(mem_info[hostip]['MemFree']) + float(mem_info[hostip]['Buffers']) + float(mem_info[hostip]['Cached'])
                Used_Mem = float(mem_info[hostip]['MemTotal']) - Free_Mem
                Rate_Mem = round(100 * Used_Mem / float(mem_info[hostip]['MemTotal']),2)
                print("Rate_Mem:", Rate_Mem)

                if Rate_Mem > int(mem_threshold):
                    msg = "服务器: %s 的内存使用率为：%s %%告警！" % (hostip, str(Rate_Mem))
                    # cust_phone = tdc.get_cust_phone(hostip)
                    # if cust_phone != None:
                    #     send_phone = cust_phone + ',13681919346'
                    #     ct.send_sms_control('NoLimit', msg, send_phone)
                    # else:
                    #     msg2 = '客户没有手机号_' + msg
                    #     ct.send_sms_control('NoLimit', msg2, '13681919346')
                    #ct.send_sms_control('NoLimit', msg, '13681919346')
                    tdc.send_cust_error_sms(hostip, msg)
                    mem_error_list.append({hostip: Rate_Mem})
                    #写库
                    mem_dic = {'inner_ip': hostip,
                            'total_mem': round(float(mem_info[hostip]['MemTotal']) / (1024 *1000), 0), 
                            'used_mem': round(Used_Mem / (1024 *1000), 0),
                            'usage': Rate_Mem,
                            'is_warning': '1',
                            'is_handled': '1' }             
                    #from myapps.tora_monitor import models as memodels
                    mmodels.MemMonitorData.objects.create(**mem_dic)
                else:
                    #写库
                    mem_dic = {'inner_ip': hostip,
                            'total_mem': round(float(mem_info[hostip]['MemTotal']) / (1024 *1000), 0), 
                            'used_mem': round(Used_Mem / (1024 *1000), 0),
                            'usage': Rate_Mem }             
                    #from myapps.tora_monitor import models as memodels
                    mmodels.MemMonitorData.objects.create(**mem_dic)

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
def one_time_task(func_name):
    return_data = {'result': False, 'data':''}
    #res = tdc.import_cust_machine()
    #res = tdc.import_node_trade_info()

    funcstr='tdc.' + func_name
    call_func = eval(funcstr)
    call_func()
    print("执行完成one_time_task任务")
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

@run_monitorJob()
def sms_control_init_task():
    return_data = {'result': False, 'data':'未成功'}
    #res = tdc.import_cust_machine()
    res = tdc.get_sms_control_data()
    # funcstr='tdc.' + func_name
    # call_func = eval(funcstr)
    # call_func()
    today = dt.datetime.now().strftime("%Y-%m-%d")

    if str(res.init_day) == today:
        return_data = {'result': True, 'data':'每日短信控制初始化成功'}
    print("执行每日短信初始化完成")
    return return_data


#fpga监控任务
@run_monitorJob()
def fpga_file_monitor():
    #print("call cust_nomrlmonot!!!")
    return_data = {'result': '', 'data':''}
    ip_list = ['192.168.9.142','192.168.10.89','192.168.10.171','10.168.8.28']
    #print("machines:", machines)
    error_list = []
    dict_error = {}
    try:
        for hostip in ip_list:
            check_res = mfpga.check_fpga_file(hostip,'root')
            if check_res != []:
                dict_error[hostip] = check_res

        if dict_error != {}:
            return_data['result'] = False
            return_data['data'] = str(dict_error)
        else:
            return_data['result'] = True
            return_data['data'] = "fpga检查正常"
    except Exception as e:
        logger.error("执行任务发生异常！",exc_info=True)
        return_data['result'] = False
        return_data['data'] = '执行任务发生异常！'

    return return_data
