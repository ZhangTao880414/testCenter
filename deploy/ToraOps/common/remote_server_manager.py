#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   remote_server_manager.py
@Time    :   2021/07/05 17:44:19
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   对远程服务器的ssh执行管理
'''

# here put the import lib
import common.common_tools as ct
import time
import datetime as dt
import os
import logging
logger = logging.getLogger()


def get_remote_ssh_command_data(hostip, username, password, command, port=22):
    
    #logger = logging.getLogger()
    yaml_path = './config/non_trade_monitor_logger.yaml'
    ct.setup_logging(yaml_path)

    # sshClient = ct.sshConnect(hostip, port, username, password)
    # if sshClient:
    # sshRes = ct.sshExecCmd(sshClient, command)
    # logger.info(hostip + "::" + command)
    # sshResList = []
    # print("sshRes:", type(sshRes),sshRes)
    try:
        sshClient = ct.sshConnect(hostip, port, username, password)
        
        sshRes = ct.sshExecCmd(sshClient, command)
        logger.info(hostip + "::" + command)
        sshResList = []
        print("sshRes:", type(sshRes),sshRes)
        for item in sshRes:
#                de_item = item.decode('gb2312')
#                error_list = de_item.strip().split(':', 1)
#                grep_lists.append(error_list)
#                memstr=','.join(error_list)
#                print memstr
#                temstr= item.strip().encode('utf-8')
            temstr = item.strip()
            sshResList.append(temstr)
            logger.info(temstr)
        ct.sshClose(sshClient)
        return sshResList
    except Exception as e:
        msg = "write failed: [hostip:%s];[username:%s];[error:%s]" % (hostip,username,str(e))
        logger.error(msg)
        return None

    finally:    
        
        logger.info("get_ssh_command_data finished")
        for handler in logger.handlers:
            logger.removeHandler(handler)

#获取系统版本
def get_os_version(hostip, username, password, os, port=22):
    if os.lower() in ['centos','redhat']:
        command = 'cat /etc/redhat-release'
        remote_data = get_remote_ssh_command_data(hostip, username, password, command)
        if remote_data != None:
            os_version = remote_data[0]
        else:
            os_version = None
    elif os.lower() in ['ubuntu']:
        command = 'cat /etc/issue'
        remote_data = get_remote_ssh_command_data(hostip, username, password, command)
        if remote_data != None:
            os_version = remote_data[0].split('\\n')[0].strip()
        else:
            os_version = None
    return os_version


#远程传文件



if __name__ == '__main__':
           
    #command = 'cat /etc/redhat-release'
    hostip = '10.188.82.107'
    username = 'hxzq'
    password = 'XXX'
    #command = 'lscpu'
    #remote_data = get_remote_ssh_command_data('192.168.238.31', 'root', 'root123', command)
    remote_data = get_os_version(hostip, username, password, os='ubuntu')
    print("remote_data:", remote_data)
    # if remote_data[0] == 'CentOS Linux release 7.6.1810 (Core)':
    #     print("系统是7.6")
    # elif remote_data[0] == 'Red Hat Enterprise Linux Server release 7.8 (Maipo)':
    #     print('7.6')
