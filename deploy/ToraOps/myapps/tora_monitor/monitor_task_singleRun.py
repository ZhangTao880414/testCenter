from django.conf import settings
import os
import sys
from functools import wraps
import datetime as dt

import django
BASE_DIR = 'D:\\my_project\\python3\\django_project\\ToraOps_project\\ToraOps'
sys.path.extend([BASE_DIR])
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ToraOps.settings')
django.setup()
#sys.path.append('..')
from myapps.toraapp import models as tmodels
from myapps.tora_monitor import models as mmodels

# Create your tests here.


class run_monitorJob(object):
    def __init__(self, logfile='./monitor.log'):
        self.logfile = logfile
 
    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            print(log_string)
            job_id = args[-1]
            tem_list = list(args)
            tem_list.pop()
            args2 = tuple(tem_list)
            print("args2:", args2)
            res = func(*args2, **kwargs)
            res = {'result': True, 'data':{"disk_size:":100, 'memory':2400, 'msg':'ok'}}
            print("monitor_job: [%s] 执行监控项:[%s]，返回结果：[%s]" % (job_id, func.__name__, str(res)))
            # # 打开logfile并写入
            # with open(self.logfile, 'a') as opened_file:
            #     # 现在将日志打到指定的文件
            #     opened_file.write(log_string + '\n')
            # 将运行结果写入MonitorJob表
            ntime = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ObjectJob = mmodels.MonitorJob.objects.filter(job_id=job_id).first()
            ObjectJob.last_runtime = ntime
            ObjectJob.last_status = res['result']
            msg = str(res['data'])
            ObjectJob.monitor_data = res['data']
            ObjectJob.save()
        return wrapped_function


def get_machine():
    machine = tmodels.ShelfMachine.objects.filter(is_active='0').first()
    print(machine, type(machine))
    print(machine.inner_ip)

@run_monitorJob()
def test_job():
    print("I am testjob1",)
    return 1


@run_monitorJob()
def test_job2(para='Job2默认参数'):
    print("我是apscheduler任务" + para)
    return 0


def get_nodeConfig(node=2):
    #node=2
    # item = 'ip_addr'
    # # tradenode = tmodels.TradeNode.objects.filter(node=node, app_type='tradeserver1', business='hxzq').first()
    # # print(tradenode.__getattribute__(item))
    # nodeobj = tmodels.NodeInfo.objects.get(pk=node)
    # print(nodeobj.node_name)
    # mq1 = nodeobj.mq.all()[0]
    # mq_name = mq1.mq_name
    # mq_obj = tmodels.ToraMq.objects.filter(mq_name=mq_name, business='hxzq', mq_type='md_L2', tele_pattern='udp').first()
    # print(mq_obj.__getattribute__(item))
    nodeConfig = {}
    for item_busi in dict(tmodels.BUSINESS_CHOICES):
        nodeConfig[item_busi] = {}
        nodeConfig[item_busi]['trade'] = {}
        nodeConfig[item_busi]['mq'] = {}
        for item_ta in dict(tmodels.APPS_CHOICES):
            nodeConfig[item_busi]['trade'][item_ta] = {}
            tradenode = tmodels.TradeNode.objects.filter(node=node, business=item_busi, app_type=item_ta).first()
            for item_value in ['ip_addr','port', 'intnet_addr', 'intnet_port']:
                if tradenode:
                    print(node,item_busi,item_ta)
                    nodeConfig[item_busi]['trade'][item_ta][item_value] = tradenode.__getattribute__(item_value)
                else:
                    nodeConfig[item_busi]['trade'][item_ta][item_value] = ''

        for item_mq in dict(tmodels.MQ_TYPE):
            nodeConfig[item_busi]['mq'][item_mq] = {}
            for item_tele in dict(tmodels.TELE_CHOICES):
                nodeConfig[item_busi]['mq'][item_mq][item_tele] = {}
                #toramq = tmodels.ToraMq.objects.filter(node=node, business=item_busi, mq_type=item_mq, tele_pattern=item_tele).first()
                nodeobj = tmodels.NodeInfo.objects.get(pk=node)
                #获取行情名字为主键
                mq1 = nodeobj.mq.all()[0]
                mq_name = mq1.mq_name
                mq_obj = tmodels.ToraMq.objects.filter(mq_name=mq_name, business=item_busi, mq_type=item_mq, tele_pattern=item_tele).first()
                for item_value in ['ip_addr','port', 'md_rec_addr', 'source_ip']:
                    if mq_obj:                   
                        print(mq_name,item_busi,item_mq,item_tele)
                        nodeConfig[item_busi]['mq'][item_mq][item_tele][item_value] = mq_obj.__getattribute__(item_value)
                    else:
                        nodeConfig[item_busi]['mq'][item_mq][item_tele][item_value] = ''

    return nodeConfig

#nodeConfig = get_nodeConfig()
#print(nodeConfig)
# dict_data = dict(tmodels.BUSINESS_CHOICES)
# print(dict_data['hxzq'])

# nodeobj = tmodels.NodeInfo.objects.get(pk=1)
# print(nodeobj.__getattribute__('node_id'))


#



def a_new_decorator(a_func):
    @wraps(a_func)
    def wrapTheFunction(*args, **kwargs):
        print("I am doing some boring work before executing a_func()")
        res = a_func(*args, **kwargs)
        if res:
            print("I am doing some boring work after executing a_func()")
        else:
            print("false....")
    return wrapTheFunction


# @a_new_decorator
# def test2(a,b):
#     print(a,b)
    

# test2('hello', 'world')

#get_machine()

# machines = tmodels.ShelfMachine.objects.filter(is_active='1')
# print(machines, type(machines))
# #print(machine.inner_ip)
# for machine in machines:
#     print(machines.values())

# ipList = tmodels.ShelfMachine.objects.filter(is_active='1').values("inner_ip")
# print(ipList)
ipList = tmodels.ShelfMachine.objects.filter(is_active='1', is_monitor='1').values('engine_room','cabinet','unit','server_model','serial_number','owner_id')
#print(ipList)
for item in ipList:
    #print(item)
    tem = item.values()
    tem2 = [str(i) for i in tem]
    sever_info = '@@'.join(tem2)
    print(sever_info)