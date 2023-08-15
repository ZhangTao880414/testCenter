#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fpga_check.py
@Time    :   2021/09/29 14:04:12
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib

import pandas as pd
import datetime as dt
import os
import logging
from common.ansible_api import ansible_execute
from myapps.tora_monitor import models as mmodels
from django.db.models import Q
import common.tora_django_common as tdc
import subprocess


logger = logging.getLogger('django')



#执行远程命令，并检查生成的文件
def check_fpga_file(hostip, rsa_user='root'):
    error_list = []
    #远程调用命令，监控脚本路径为 /home/jindayu/monitor/monitor.sh
    command = "/home/jindayu/monitor/monitor.sh"
    shell_data = ansible_execute(hostip, 'shell', command, rsa_user)
    print(shell_data)

    #日志模板路径为 /home/jindayu/monitor/template.csv 
    #日志文件路径为 /home/jindayu/monitor/fpga_log.csv 
    #把文件取到本地来进行比较
    temp_file_dir = '/home/trade/tora_ops/ToraOps/myapps/tora_monitor/job_scripts/fpga_temp'
    if os.path.exists(temp_file_dir):
        pass
    else:
        os.mkdir(temp_file_dir)
    files = ["/home/jindayu/monitor/template.csv","/home/jindayu/monitor/fpga_log.csv"]
    # for get_file in files:
    #     args = "src=%s dest=%s" % (get_file, temp_file_dir)
    #     get_file_res = ansible_execute(hostip, 'fetch', args, rsa_user)
    #scp取文件
    #fetch_command = "scp root@192.168.10.171:/home/jindayu/monitor/template.csv /tmp/template.csv"
    for get_file in files:
        fetch_command = "scp {0}@{1}:{2} {3}/{1}/".format(rsa_user,hostip,get_file,temp_file_dir)
        logger.info(fetch_command)
        res = subprocess.run(fetch_command,shell=True,check=True,capture_output=True)
        logger.info(str(res.returncode))
        logger.info(res.stdout.decode('utf-8'))
        res_error = res.stderr.decode('utf-8')
        if res_error:
            logger.error(res_error)
            msg = "Error,服务器[%s]取文件[%s]失败，错误消息：[%s]" % (hostip,get_file,res_error)
            #ct.send_sms_control('NoLimit', msg)
            tdc.send_cust_error_sms(hostip, msg)
        else:
            msg = "Ok,服务器[%s]上取文件[%s]成功" % (hostip,get_file)
            logger.info(msg)

    
    # temp_file = temp_file_dir + '/' + hostip + '/home/jindayu/monitor/template.csv'
    # fpga_log_file = temp_file_dir + '/' + hostip + '/home/jindayu/monitor/fpga_log.csv'
    temp_file = temp_file_dir + '/' + hostip + '/template.csv'
    fpga_log_file = temp_file_dir + '/' + hostip + '/fpga_log.csv'
    temp_df = pd.read_csv(temp_file)
    #print(temp_df)
    fpga_df = pd.read_csv(fpga_log_file, header=None, names=['NAME','NEW_VALUE'])
    #print(fpga_df)
    merge_df = pd.merge(temp_df, fpga_df)
    #print(merge_df)
    check_df = merge_df.loc[merge_df['BOUND'] == 1]
    print(check_df)
    now_time = dt.datetime.now().strftime('%H:%M:%S')
    for row in check_df.itertuples():
        NAME = getattr(row, 'NAME')
        TYPE = getattr(row, 'TYPE')
        BOUND = int(getattr(row, 'BOUND'))
        STARTTIME = getattr(row, 'STARTTIME')
        ENDTIME = getattr(row, 'ENDTIME')
        # LOWERLIMIT = getattr(row, 'LOWERLIMIT')
        # UPPERLIMIT = getattr(row, 'UPPERLIMIT')
        INCREMENT = int(getattr(row, 'INCREMENT'))
        #print("INCREMENT:",INCREMENT)
        if TYPE == 'INTEGER':
            LOWERLIMIT = int(getattr(row, 'LOWERLIMIT'))
            UPPERLIMIT = int(getattr(row, 'UPPERLIMIT'))
            NEW_VALUE = int(getattr(row, 'NEW_VALUE'))
        else:
            LOWERLIMIT = getattr(row, 'LOWERLIMIT')
            UPPERLIMIT = getattr(row, 'UPPERLIMIT')
            NEW_VALUE = getattr(row, 'NEW_VALUE')
        is_warning = '0'
        is_handled = '0'

        #print(now_time, now_time>STARTTIME, now_time<=ENDTIME)
        time_check = (now_time > STARTTIME and now_time < '11:30:00') or (now_time > '13:00:00' and now_time < ENDTIME)
        if time_check and str(BOUND) == '1':
            if str(INCREMENT) == '1':
                #get_last_value
                last_value = get_last_fpga_value(hostip,NAME)
                #last_value = 109937091
                if last_value == None:
                    logger.info("应该是第一次当天还没有数据不检查")
                else:
                    if int(NEW_VALUE) > int(last_value):
                        print("数据发生了递增，正常！")
                    else:
                        msg = '服务器%s,数据项：%s的值 %s 距上一次到现在没有递增！' % (hostip,NAME,str(NEW_VALUE))
                        tdc.send_cust_error_sms(hostip, msg)
                        logger.error(msg)
                        is_warning = '1'
                        is_handled = '1'
                        error_list.append((NAME,int(last_value),NEW_VALUE))
            if TYPE in ['INTEGER','FLOAT']:
                if float(NEW_VALUE) >= LOWERLIMIT and float(NEW_VALUE) <= UPPERLIMIT:
                    print("正常")
                else:
                    msg = "服务器%s的fpga数据项%s是:%s不在区间内[%s,%s]" % (hostip,NAME,str(NEW_VALUE),str(LOWERLIMIT),str(UPPERLIMIT))
                    tdc.send_cust_error_sms(hostip, msg)
                    logger.error(msg)
                    is_warning = '1'
                    is_handled = '1'
                    error_list.append((NAME,LOWERLIMIT,UPPERLIMIT,NEW_VALUE))
        else:
            print("不用检查")
        #写库
        dic = {'inner_ip': hostip,
            'para_name': NAME, 
            'para_type': TYPE,
            'para_value': str(NEW_VALUE),
            'bound': str(BOUND),
            'start_time': STARTTIME,  
            'end_time': ENDTIME,
            'lower_limit': str(LOWERLIMIT),
            'upper_limit': str(UPPERLIMIT),
            'increment': str(INCREMENT),
            'is_warning': is_warning,
            'is_handled': is_handled}                          
        mmodels.FpgaMonitorData.objects.create(**dic)

    return error_list


def get_last_fpga_value(hostip,NAME):

    day_time = dt.date.today().strftime("%Y-%m-%d %H:%M:%S")
    fpga_obj = mmodels.FpgaMonitorData.objects.filter(Q(inner_ip=hostip), 
                                                      Q(para_name=NAME),
                                                      Q(create_time__gt=day_time)).last()
    
    print("fpga_obj:",fpga_obj)
    if fpga_obj:
        return fpga_obj.__getattribute__('para_value')
    else:
        return None
    #return 1



if __name__ == "__main__":
    res = check_fpga_file('192.168.9.142')
    print(res)
