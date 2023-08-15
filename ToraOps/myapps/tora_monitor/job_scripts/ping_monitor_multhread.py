# -*- coding: utf-8 -*-
"""
Created on 2019-07-26 10:01:58

@author: zhangwei
@comment:非交易时间监控
##### 1.物理机存活状态

###### 地址是否可以ping通
20201009：采用多线程的处理方式


"""

import time
#import threading
import datetime as dt
#import common_tools as ct
import platform
import sys
import getopt
import logging
import json
import os
import subprocess
import pandas as pd
#import threading
from multiprocessing.dummy import Pool as ThreadPool

# import django
# BASE_DIR = 'D:\\my_project\\python3\\django_project\\ToraOps_project\\ToraOps'
# sys.path.extend([BASE_DIR])
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ToraOps.settings')
# django.setup()

import common.common_tools as ct
from myapps.toraapp import models as tmodels
from myapps.tora_monitor import models as mmodels


logger = logging.getLogger('django')
error_list = []

 
'''
Ping监控
'''
def ping_server_info(info):
    
    hostip = info['inner_ip']
    print(hostip)
    # columns_list = info[1].index.tolist()
    # server_info_list = []
    # server_cols = ('engine_room','cabinet','unit','server_model','serial_number')
    # for col in server_cols:
    #     if col in columns_list:
    #         server_info_list.append(info[1][col])
    # #物理信息
    # server_info = hostip + '@' + '@'.join(server_info_list)
    infoValues = info.values()
    machineValues = [str(i) for i in infoValues]
    server_info = '@@'.join(machineValues)
    result = {'server_info':server_info, 'data':{}}
    #print(server_info)
    ping_info_verify = False
    sysstr = platform.system()
    logger.info('ping ' + hostip)
    if sysstr == "Windows":
        ping = subprocess.Popen('ping ' + hostip,
                                shell=True,
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE) # 执行命令
        res,err = ping.communicate()
#            print("err:", err.decode('gbk'))
#            if err: sys.exit(err.decode('gbk').strip('\n'))
        if err:
            logger.info("ping error: %s" % str(err))
            pres = []
        else:
            pres = list(res.decode('gbk').split('\n'))
            logger.debug("pres:" + str(pres))
        try:
            loss = pres[8].split('(')[1].split('%')[0] + "%"  # 获取丢包率
        except IndexError:
            loss = "100%"       
        try:
            rtt = float(pres[10].split('=')[3].split('ms')[0]) # 获取rtt avg值
        except IndexError:
            rtt = 9999
    else:
#        ping = subprocess.Popen('ping -i 0.2 -c 4 -q -I ' + src + ' ' + dest,
        #-I<网络界面> 使用指定的网络接口送出数据包
        ping = subprocess.Popen('ping -i 1 -c 4 -q ' + hostip,
                                shell=True,
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE) # 执行命令
        res,err = ping.communicate()
#            print("err:", err.decode('gbk'))
#            if err: sys.exit(err.decode('gbk').strip('\n'))
        if err:
            logger.info("ping error: %s" % str(err))
            pres = []
        else:
            pres = list(res.decode('gbk').split('\n'))   
            logger.debug("pres:" + str(pres))
        try:
            #tem = "4 packets transmitted, 0 received, 100% packet loss, time 611ms"
            loss = pres[3].split()[5]  # 获取丢包率
            #loss = tem.split()[5]
        except IndexError:
            loss = "100%"
        try:
            rtt = float(pres[4].split('/')[4]) # 获取rtt avg值            
        except IndexError:
            rtt = 9999
    result['data']['loss'] = loss
    result['data']['rtt'] = rtt
    # # loss>0,rtt>800报警
    # if float(loss.strip('%')) > 0 or float(rtt) > 800 :
    #     ping_info_verify = False
    #     msg = "error:" + hostip + "::The ping lost is " + loss + ", rtt is " + rtt + " ms, Server info: " + server_info
    #     logger.error(msg)
    #     ct.send_sms_control("ping", msg)
    #     error_list.append(hostip)
    # else:
    #     ping_info_verify = True
    #     msg = "ok:" + hostip + "::The ping lost is " + loss + ", rtt is " + rtt + " ms"
    #     logger.info(msg)
    # msg = "Ping Check Result: " + str(ping_info_verify)
    # logger.info(msg)

    return result


#ping监控
def ping_monitor_task(verify={"loss": 0, "rtt": 800}):

    # pddata = pd.read_csv('./config/cust_server_list.csv',encoding='gbk')
    # #如果有过滤参数'is_monitor'，则过滤需要监控的记录
    # pd_columns = pddata.columns.values.tolist()
    # if 'is_monitor' in pd_columns:
    #     sort_df = pddata[pddata['is_monitor'] !=0 ]
    #     sort_df.fillna('Empty', inplace=True)
    # else:
    #     sort_df = pddata
    ping_machineList = tmodels.ShelfMachine.objects.filter(is_active='1', is_monitor='1').values('inner_ip', 'engine_room','cabinet','unit','server_model','serial_number','owner_id')
    error_list = []
    try:
        logger.info("The Ping monitor Starting...")
        start = time.time()
        pool = ThreadPool(20) # 这里加一个参数即可
        #check_result_list = pool.map(ping_server_info, sort_df.iterrows())
        check_result_list = pool.map(ping_server_info, ping_machineList)
        logger.info('threadpool total: ' + str(time.time() - start) + ' seconds')
        print("return_list:",check_result_list)
        
        logger.info("The Ping monitor Stoped") 
        for result in check_result_list:
            hostip = result['server_info'].split('@@')[0]
            if float(result['data']['loss'].strip('%')) > verify['loss'] or result['data']['rtt'] > verify['rtt'] :
                ping_info_verify = False
                msg = "error: The ping lost is %s, rtt is %6.3f ms. Server info: %s::" % \
                     (result['data']['loss'], result['data']['rtt'], result['server_info'],)
                logger.error(msg)
                ct.send_sms_control("ping", msg)
                error_list.append(result)
            else:
                ping_info_verify = True
                msg = "ok: The ping lost is %s, rtt is %6.3f ms. Server info: %s" % \
                    (result['data']['loss'], result['data']['rtt'], result['server_info'])
                logger.info(msg)
            print(error_list)
    
    except Exception as e:
        #print(str(e))
        msg = str(e)
        logger.error(msg)
        return -1
    
    return error_list




def main(argv):
    
    try:
        yaml_path = './config/non_trade_monitor_logger.yaml'
        ct.setup_logging(yaml_path)
        #获得log_file目录，不要改变yaml的root设置info_file_handler位置设置，不然获取可能失败
        # t = logger.handlers
        # log_file = t[1].baseFilename
#        print(log_file)
#        log_file = './mylog/non_trade_monitor_run.log'
        #初始化参数表
        # ct.init_sms_control_data()
        manual_task = 'ping'
        try:
            opts, args = getopt.getopt(argv,"ht:",["task="])
        except getopt.GetoptError:
            print('non_trade_monitor.py -t <task> or you can use -h for help')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print('non_trade_monitor.py -t <task>\n \
                    (default:python non_trade_monitor.py) means auto work by loops. \n \
                    use -t can input the manul single task.\n \
                    task=["ps","mem","ping","disk","core"].  \n \
                    task="ps" means porcess monitor  \n \
                    task="mem" means memory monitor  \n \
                    task="ping" means ping server monitor  \n \
                    task="disk" means disk monitor  \n \
                    task="core" means core file monitor  \n \
                    task="sjdr" means sjdr folder Order file monitor  ' )            
                sys.exit()
            elif opt in ("-t", "--task"):
                manual_task = arg
            if manual_task not in ["ps","mem","ping","disk","core","xwdm","aft_cleanup","bef_cleanup","sjdr","follow","bkdb","clean_dblog","self_monitor","ssh_connect","ssh_excute","exch_file"]:
                logger.info("[task] input is wrong, please try again!")
                sys.exit()
            logger.info('manual_task is:%s' % manual_task)
    #    if inc == 0:
        #task=["ps_port","mem","fpga","db_init","db_trade","errorLog"]
        if manual_task == 'ping':
            logger.info("Start to excute the ping server monitor")
            ping_monitor_task()
        else:
            # 只执行一次的任务，fpga监控，数据库资金等信息监控
#            fpga_task()
#            db_init_monitor_task()
            print("input error")
            sys.exit()

    except Exception:
        logger.error('Faild to run non_trade_monitor!', exc_info=True)
    finally:
        for handler in logger.handlers:
            logger.removeHandler(handler)



if __name__ == '__main__':
    main(sys.argv[1:])

