#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   share_server_choice.py
@Time    :   2021/04/18 17:25:40
@Author  :   wei.zhang
@Contact :   158279489@qq.com
@Department   :  XXX
@Desc    :   None
'''

# here put the import lib

from myapps.toraapp import models as tmodels
from django.db.models import Q
import pandas as pd



        # if os[:6].lower not in['redhat','centos','ubuntu','linux']:
        #     print("不自动处理资源")

def choice_share_server(engine_room, os, os_version, node_no):
    #查询可用服务器
    #s = tmodels.ShareServerInfo.objects.filter(Q(engine_room='dgnf') & Q(machine__node__node_no='7'))
    #s = tmodels.ShareServerInfo.objects.filter(machine__node__node_no='7')
    serverSet = tmodels.ShareServerInfo.objects.filter(Q(machine__node__node_no=node_no),
                                                       Q(machine__os='redhat') | Q(machine__os='centos') | Q(machine__os='ubuntu'))

    if len(s) == 0:
        print("该节点没有linux共有服务器")
    else:
        match_server=[]
        for server in serverSet:
            dict_data = {}   
            dict_data['inner_ip'] = server.machine__inner_ip
            dict_data['os'] = server.machine__os
            dict_data['os_version'] = server__machine__os_version
            dict_data['assigned_count'] = server.assigned_count
            match_server.append(dict_data)
        #if os in ['centos','redhat','linux']:
        ubuntu_server = []
        full_match_server = []
        os_match_server = []
        linux_match_server = []
        for server_dict in match_server:
            # if server_dict['os'] == 'ubuntu':
            #     ubuntu_server.append(server_dict)
            if server_dict['os'] == os and server_dict['os_version'] == os_version:
                full_match_server.append(server_dict)
            elif server_dict['os'] == os:
                os_match_server.append(server_dict)
            # elif server_dict['os'] == 'ubuntu':
            #     ubuntu_server.append(server_dict)
            else:
                print("系统不匹配的linux服务器！")
                linux_match_server.append(server_dict)
        # else:
        #     print("ubuntu的暂不做自动处理")

        if os != 'ubuntu':

            if len(full_match_server) != 0 :
                inner_ip = get_min_assigned_server(full_match_server)    
            elif len(os_match_server) != 0 :
                print("版本不对任选一个")
                inner_ip = get_min_assigned_server(os_match_server)
            else:
                for server in linux_match_server:
                    red_linux_server = []
                    if server['os'] != 'ubuntu':
                        red_linux_server.append(server)
                if len(red_linux_server) != 0 :
                    inner_ip = get_min_assigned_server(red_linux_server)
                else:
                    inner_ip = None
        else:
            if len(full_match_server) != 0 :
                inner_ip = get_min_assigned_server(full_match_server)    
            elif len(os_match_server) != 0 :
                print("版本不对任选一个")
                inner_ip = get_min_assigned_server(os_match_server)
            else:
                print("系统不匹配的ubuntu不做自动选择")
                inner_ip = None

            

def get_min_assigned_server(match_server):
    df = pd.DataFrame(match_server)
    print(df)
    return (df['inner_ip'][df['assigned_count'] == df['assigned_count'].min()].values[0])
            

match_server = [{'inner_ip': '192.168.10.111', 'assigned_count': 3}, 
                {'inner_ip': '192.168.10.114', 'assigned_count': 5},
                {'inner_ip': '192.168.10.116', 'assigned_count': 2}]

get_min_assigned_server(match_server)

# os = 'CentoS 79s'
# print(os[:6].lower())