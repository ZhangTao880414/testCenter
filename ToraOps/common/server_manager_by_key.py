#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   server_manager_by_key.py
@Time    :   2021/04/01 10:52:12
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib
import pandas as pd
import numpy as np
import re
import json
import datetime as dt
import logging
#import mysql_tools_class as myc
import common_tools as ct
import no_pass_ssh as nssh
import os
import random
import string
# from ansible_api import ansible_execute

# from myapps.toraapp import models as tmodels
# from django.db import connection, transaction


logger = logging.getLogger('django')


#通过ansible对免密认证的服务器创建多个个用户，并写入数据库
#def create_n_users(engine_room,hostip,user_no):
# def create_n_users(queryset):
#     user_no = 20
#     error_ip = []
#     for server in queryset:
#         # print("server.machine", server.machine, type(server.machine))
#         print(server.machine.inner_ip)
#         hostip = server.machine.inner_ip
#         filename = './common/csv/users' + '_' + hostip + '.csv'
#         if os.path.exists(filename):
#             err_msg = "%s已经存在了，请确认后再增加用户！" % filename
#             logger.error(err_msg)
#             error_ip.append(hostip)
#             continue
#         ct.write_file(filename,'hostip,sys_user_name,sys_user_passwd')
#         #mysql_obj = myc.mysql_tools(mysqldb_info)
#         res_list = []
#         for i in range(user_no):
#             s = "%02d" % (i+1)
#             sys_user_name = 'TestUser' + s
#             #生成密码
#             random.seed()
#             chars = string.ascii_letters + string.digits + '@' + '#' + '$' + '!'
#             #print([''.join([random.choice(chars) for _ in range(8)]) for _ in range(1)])
#             #密码位数10
#             sys_user_passwd = ''.join([random.choice(chars) for _ in range(10)])
#             print(sys_user_name,sys_user_passwd)
#             ct.write_file(filename, hostip + ',' + sys_user_name + ',' + sys_user_passwd)
#             dict_data = {"hostip":hostip,"user":sys_user_name,"passwd":sys_user_passwd}
#             json_data = json.dumps(dict_data, ensure_ascii=False)
#             print(json_data)
#             #创建用户
#             #ansible-playbook createuser_by_para.yml -e '{"hostip":"192.168.238.21","user":"user1","passwd":"abc"}'
#             command = "ansible-playbook ./common/createuser_by_para.yml -e '%s'" % str(json_data)
#             print(command)
#             exec_res = os.popen(command).readlines()
#             logger.info("exec_res:")
#             logger.info(exec_res)
#             sshResList = []
#             for item in exec_res:
#                 if item == '\n':
#                     print("换行")
#                 else:
#                     sshResList.append(item)
#             #最后一行是ansible的执行结果
#             print(len(sshResList),sshResList)
#             if ':' in sshResList[-1]:
#                 last_ret = (sshResList[-1].split(':')[1]).split()
#             else:
#                 logger.error("playbook未执行！")
#                 continue
#             #last_ret = ['ok=2', 'changed=1', 'unreachable=0', 'failed=0', 'skipped=0', 'rescued=0', 'ignored=0']
#             res_dict = {}
#             for item in last_ret:
#                 tem = item.split('=')
#                 key = tem[0]
#                 value = tem[1]
#                 res_dict[key] = int(value)
#             print(res_dict)

#             if res_dict['unreachable'] != 0 or res_dict['failed'] != 0:
#             # if False:
#                 logger.error("ansible-playbook执行失败!")
#                 error_ip.append(hostip)
#             else:
#                 #执行成功，写入数据库
#                 now_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 insert_users_sql = "INSERT INTO toraapp_systemuserinfo(engine_room,inner_ip,sys_user_name,sys_user_passwd,cur_status,nsight_user,create_time,update_time,operator_id) \
#                     VALUES ('%s','%s','%s', '%s','%s','%s','%s','%s','%s')" % \
#                     (server.engine_room,hostip,sys_user_name,sys_user_passwd,'0','',now_time,now_time,'1')
#                 # res = mysql_obj.execute_sql_noclose(insert_users_sql)
#                 cursor = connection.cursor()  # 获得一个游标(cursor)对象
#                 res = cursor.execute(insert_users_sql)
#                 logger.info(res)
#                 res_list.append(res)
#     if len(error_ip) != 0:
#         msg = "执行批量创建用户错误的IP：" + ','.join(error_ip)
#         logger.error(msg)
#         return {'code':0, 'data': error_ip}
#     else:
#         return {'code':1, 'data':'success'}


def get_system_info(hostip):
    setup_dict = ansible_execute([hostip],'setup','')
    logger.info(setup_dict)
    data = {}
    for key in setup_dict.keys():
        #key为IP
        data[key] = {}
        if 'ok' in setup_dict[key].keys():
            temp_data = setup_dict[key]['ok']['ansible_facts']['ansible_lsb']
            print(temp_data)
            sn = setup_dict[key]['ok']['ansible_facts']['ansible_product_serial']
            host_name = setup_dict[key]['ok']['ansible_facts']['ansible_hostname']

            # description = setup_dict[key]['ok']['ansible_facts']['ansible_lsb']['description']
            # ansible_machine = setup_dict[key]['ok']['ansible_facts']['ansible_machine']
            # sysinfo = '%s %s' % (description, ansible_machine)

            os = setup_dict[key]['ok']['ansible_facts']['ansible_os_family']
            os_version = setup_dict[key]['ok']['ansible_facts']['ansible_distribution_version']
            os_kernel = setup_dict[key]['ok']['ansible_facts']['ansible_kernel']
            cpu_endor = setup_dict[key]['ok']['ansible_facts']['ansible_processor'][1]
            cpu_model = setup_dict[key]['ok']['ansible_facts']['ansible_processor'][2]
            cpu_count = setup_dict[key]['ok']['ansible_facts']['ansible_processor_count']
            single_cpu_cores = setup_dict[key]['ok']['ansible_facts']['ansible_processor_cores']
            mem = setup_dict[key]['ok']['ansible_facts']['ansible_memtotal_mb']
            memfree = setup_dict[key]['ok']['ansible_facts']['ansible_memfree_mb']
            ipadd_in = setup_dict[key]['ok']['ansible_facts']['ansible_all_ipv4_addresses'][0]
            disk_size = setup_dict[key]['ok']['ansible_facts']['ansible_devices']['sda']['size']

            ipv4_addresses = setup_dict[key]['ok']['ansible_facts']['ansible_all_ipv4_addresses']
            print(ipv4_addresses)
            data[key]['sn'] = sn
            #data[key]['sysinfo'] = sysinfo
            data[key]['os'] = os
            data[key]['os_version'] = os_version
            data[key]['cpu_model'] = cpu_model
            #data[key]['cpu_count'] = cpu_count
            data[key]['cpu_cores'] = single_cpu_cores * cpu_count
            data[key]['mem'] = str(mem) + ' MB'
            data[key]['memfree'] = str(memfree) + ' MB'
            data[key]['disk'] = disk_size
            #data[key]['ipadd_in'] = ipadd_in
            data[key]['all_ipv4_addresses'] = ipv4_addresses
            data[key]['os_kernel'] = os_kernel
            data[key]['host_name'] = host_name
        #elif 'unreachable' in setup_dict[key].keys():
        else:
            data[key] = {}
    #print(data)
    return data



#内存和cpu频率监控
#dmidecode -t memory | grep 'Configured Clock Speed'
#cat /proc/cpuinfo | grep 'cpu MHz' &  lscpu | grep 'CPU MHz'
def get_freq_info(hostip):
    #results_callback = ansible_execute([hostip],'shell','ls','root')
    shell_dict = {'dmidecode': "dmidecode -t memory | grep 'Configured Clock Speed'",'cpuinfo': "cat /proc/cpuinfo | grep 'cpu MHz'", 'lscpu': "lscpu | grep 'CPU MHz'"}
    freq_dict = {}
    for shell_key in shell_dict.keys():
        freq_dict[shell_key] = {}
        setup_dict = ansible_execute(hostip,'shell',shell_dict[shell_key],'root')
        logger.info(setup_dict)
        for ip in setup_dict.keys():
            #freq_dict[key][key2] = []
            if 'ok' in setup_dict[ip].keys():
                stdout = setup_dict[ip]['ok']['stdout_lines']
                #print(type(stdout),len(stdout))
                #tem_list = str(stdout).split('')
                #处理stdout数据
                res_list = []
                for item in stdout:
                    #print("item:",item)
                    if '：' in item:
                        data = item.split('：')[1].strip()
                        #print("data:",data)
                    else:
                        data = item.split(':')[1].strip()
                    res_list.append(data)
                freq_dict[shell_key][ip] = res_list
            else:
                freq_dict[shell_key][ip] = []
    return freq_dict
    #resu = {'code': 200, 'message': '登录成功'}
    #res_json = json.dumps(resu, ensure_ascii=False)

#获取大于阈值threshold的磁盘情况
def get_disk_info(hostip, threshold):
    disk_dict = {}
    disk_shell = "df -hP|awk 'NR>1 && int($5) > {0}'".format(threshold)
    shell_data = ansible_execute(hostip, 'shell', disk_shell, 'root')
    for ip in shell_data.keys():
                #freq_dict[key][key2] = []
                if 'ok' in shell_data[ip].keys():
                    stdout = shell_data[ip]['ok']['stdout_lines']
                    #print("stdout:",type(stdout),len(stdout))
                    #处理stdout数据
                    #item_dict = {}
                    res_list = []
                    for item in stdout:
                        #print("item:",item)
                        # if '：' in item:
                        #     data = item.split('：')[1].strip()
                        #     #print("data:",data)
                        # else:
                        #     data = item.split(':')[1].strip()
                        #"Filesystem,Size,Used,Avail,Use%,Mounted on"
                        disklist = item.strip().split()
                        print("disklist:", disklist)
                        Use_Rate = int(disklist[4].split('%')[0])
                        logger.info("Use_Rate:" + disklist[4])
                        # if len(disklist) == 6:
                        #     item_dict['FileSystem'] = disklist[0]
                        #     item_dict['Size'] = disklist[1]
                        #     item_dict['Used'] = disklist[2]
                        #     item_dict['Avail'] = disklist[3]
                        #     item_dict['Use'] = disklist[4]
                        #     item_dict['MountedOn'] = disklist[5]
                        # else:
                        #     logger.error("disklist 格式不对，没法处理！")
                        
                        #匹配网络路径
                        matchObj = re.search( r'//.*?/', disklist[0], re.M|re.I)            
                        #去掉mnt/cdrom和//ip/path这样的文件
                        if (disklist[0] not in ["/dev/sr0","/dev/sr1","/dev/loop0"]) and not(matchObj):
                            res_list.append(disklist)
                            
                        else:
                            logger.info("%s磁盘不需要报警！" % disklist[0])
                    disk_dict[ip] = res_list
                else:
                    disk_dict[ip] = []
    return disk_dict


def get_mem_info(hostip):
    mem_dict = {}
    mem_shell = 'cat /proc/meminfo'
    shell_data = ansible_execute(hostip, 'shell', mem_shell, 'root')
    for ip in shell_data.keys():
            #freq_dict[key][key2] = []
            if 'ok' in shell_data[ip].keys():
                stdout = shell_data[ip]['ok']['stdout_lines']
                print("stdout:", stdout)
                mem_list = []
                for item in stdout:
                    #print("item:",item)
                    item_tuples = re.findall("(.*?): .*?(\d+)", item)
                    #print("item_tuple:", item_tuples)
                    mem_list.append(item_tuples[0])
                #print("mem_list:", mem_list)
                full_dict = dict(mem_list)
                check_dict = {}
                for key in ['MemTotal','MemFree','MemAvailable','Buffers','Cached','SwapCached','SwapTotal','SwapFree']:
                    check_dict[key] = full_dict[key]
                mem_dict[ip] = check_dict
            else:
                mem_dict[ip] = {}
    return mem_dict


if __name__=='__main__':
    #data = get_disk_info('192.168.10.214', 85)
    data = get_mem_info('192.168.10.214')
    print(len(data), data)