#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tora_django_common.py
@Time    :   2021/01/29 10:34:48
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib

#from myapps.toraapp.models import ShelfMachine, ToraCustomer, NodeInfo, TradeNode, ToraMq SystemUserInfo, ROOM_CHOICES
from myapps.toraapp import models as tmodels
import datetime as dt
import common_tools as ct
import vpn_manager as vpnm
import upgrade_console as upgc
from multiprocessing.dummy import Pool as ThreadPool
import logging
import os
import json
from django.conf import settings
from django.core.mail import send_mail
from threading import Thread
from django.db import connection, transaction
from django.db.models import Q
import pandas as pd
import subprocess
#import sms_control as smsc


logger = logging.getLogger('django')


def get_engineRoomStr(engine_room):
        # ROOM_CHOICES = (
    #         ('shwp', u'上海宛平'),
    #         ('shnq', u'上海宁桥'),
    #         ('shgq', u'上海外高桥'),
    #         ('shjq', u'上海金桥'),
    #         ('shkj', u'上海科技网'),
    #         ('shxtl', u'上海斜土路'),
    #         ('dgnf', u'东莞南方'),
    # )
    # engine_room = 'dgnf'

    for item in tmodels.ROOM_CHOICES:
        for index in range(len(item)):
            if item[0] == engine_room :
                return item[1]
    return engine_room

#根据节点的ID查询对应交易和行情信息
def get_nodeConfig(node):
    
    nodeConfig = {}
    for item_busi in dict(tmodels.BUSINESS_CHOICES):
        nodeConfig[item_busi] = {}
        nodeConfig[item_busi]['trade'] = {}
        nodeConfig[item_busi]['mq'] = {}
        for item_ta in dict(tmodels.APPS_CHOICES):
            nodeConfig[item_busi]['trade'][item_ta] = {}
            tradenode = tmodels.TradeNode.objects.filter(node=node, business=item_busi, app_type=item_ta).first()
            for item_value in ['ip_addr','port', 'internet_addr_ports']:
                if tradenode:
                    print(node,item_busi,item_ta)
                    nodeConfig[item_busi]['trade'][item_ta][item_value] = tradenode.__getattribute__(item_value)
                else:
                    nodeConfig[item_busi]['trade'][item_ta][item_value] = ''
        
        nodeobj = tmodels.NodeInfo.objects.get(pk=node)
        node_no = nodeobj.__getattribute__('node_no')

        for item_mq in dict(tmodels.MQ_TYPE):
            nodeConfig[item_busi]['mq'][item_mq] = {}
            #for item_tele in dict(tmodels.TELE_CHOICES):
            for register_type in dict(tmodels.REGISTER_CHOICES):
                nodeConfig[item_busi]['mq'][item_mq][register_type] = {}
                nodeobj = tmodels.NodeInfo.objects.get(pk=node)
                #先按照my_type和register_type过滤结果
                mq_objs = tmodels.ToraMq.objects.filter(mq_type=item_mq, register_type=register_type)
                
                for item_value in ['tele_pattern','ip_addr','port','md_rec_addr','source_ip']:
                    nodeConfig[item_busi]['mq'][item_mq][register_type][item_value] = ''
                    for mq_obj in mq_objs:
                        print("1111:", mq_obj.node_nos, mq_obj.business)
                        node_list = (mq_obj.node_nos).split(';')
                        business_list = list(mq_obj.business)
                        #找到该节点该业务的行情配置项
                        if (node_no in node_list ) and (item_busi in business_list):
                                nodeConfig[item_busi]['mq'][item_mq][register_type][item_value] = mq_obj.__getattribute__(item_value)


    return nodeConfig

def get_vpnInfo(engine_room):
    # if engine_room == 'dgnf':
    #     return{'vpn_address':'https://125.93.72.195/','vpn_passwd':'hxzq123'}
    # elif engine_room == 'shnq':
    #     return{'vpn_address':'https://101.226.250.250/','vpn_passwd':'hxzq123'}
    # elif engine_room == 'shwp':
    #     return{'vpn_address':'https://101.230.205.158/','vpn_passwd':'hxzq123'}
    # else :
    #     return{'vpn_address':'https://101.230.205.158/','vpn_passwd':'hxzq123'}
    vpn_cfg = tmodels.VpnCfgInfo.objects.filter(engine_room=engine_room).first()
    if vpn_cfg:
        return {'vpn_address':vpn_cfg.vpn_address, 'vpn_passwd':vpn_cfg.vpn_init_passwd}
    else:
        return None

#同步vpn数据到django库
def dump_vpn_users():
    pass

def query_vpn_user(engine_room, vpn_user_name):
    vm = vpnm.vpn_manager(engine_room)
    exist_user = vm.search_exit_user(vpn_user_name)

    if exist_user == False :
        logger.info("vpn用户%s不存在" % vpn_user_name)
        return 0
    else:
        logger.info("vpn用户%s已存在" % vpn_user_name)
        return 1

#创建用户并关联资源
def add_vpnuser_resource(engine_room, custgroup_name, vpn_user_name, vpn_phone, inner_ip, os):
    #查询vpn是否存在，不存在调自动创建接口
    vm = vpnm.vpn_manager(engine_room)
    exist_user = vm.search_exit_user(vpn_user_name)

    if exist_user == False :
        logger.info("vpn用户%s不存在，需要创建" % vpn_user_name)
        vpn_info = get_vpnInfo(engine_room)
        vpn_init_passwd = vpn_info['vpn_passwd']
        res_code = vm.add_new_user(vpn_user_name, vpn_phone, vpn_init_passwd, custgroup_name)
    else:
        logger.info("vpn用户%s已存在，不需要创建" % vpn_user_name)
        res_code = 0

    exist_res = vm.get_rec_data_cloud(inner_ip)
    if exist_res == False :
        logger.info("服务器资源%s不存在，需要创建" % inner_ip)
        rec_code = vm.add_new_rec(inner_ip, os)
    else:
        logger.info("服务器资源%s已存在，不需要创建" % inner_ip)
        rec_code = 0  

    exist_role = vm.get_role_data_cloud(inner_ip)
    if exist_role == False :
        logger.info("角色授权%s不存在，需要创建" % inner_ip)
        role_code = vm.add_role_cloud(inner_ip, vpn_user_name, inner_ip)
    else:
        logger.info("角色授权%s已存在，不需要创建" % inner_ip)
        add_flag = True
        role_code = vm.update_role_cloud(inner_ip, vpn_user_name, inner_ip, add_flag)

    if res_code == 0 and role_code == 0 and rec_code == 0 :
        msg = "机房%s,创建vpn用户:%s,资源：%s 成功" % (engine_room, vpn_user_name, inner_ip)
        logger.info(msg)
        add_django_VpnInfo(engine_room, vpn_user_name, vpn_phone, inner_ip, custgroup_name, os)
        res = 1
    else:
        msg = "机房%s,创建vpn用户:%s,资源：%s 失败" % (engine_room, vpn_user_name, inner_ip)
        logger.error(msg)
        send_res = send_mail(msg, msg, 'zhangwei@n-sight.com.cn',
                    settings.Tora_Oper_Group, fail_silently=False)
        ct.send_sms_control('NoLimit', msg, '13681919346')
        res = 0  
    return res

#释放vpn账号和资源对应关系
def release_vpnuser_resource(engine_room, custgroup_name, vpn_user_name, vpn_phone, inner_ip):
    vm = vpnm.vpn_manager(engine_room)
    # exist_rec = vm.get_rec_data_cloud(inner_ip)
    # if exist_rec == False :
    #     logger.info("服务器资源%s不存在，需要创建" % inner_ip)
    #     rec_code = vm.add_new_rec(inner_ip, os)
    # else:
    #     logger.info("服务器资源%s已存在，不需要创建" % inner_ip)
    #     rec_code = 0  

    exist_role = vm.get_role_data_cloud(inner_ip)
    if exist_role == False :
        logger.info("角色授权%s不存在，没法自动处理释放资源" % custgroup_name)
        role_code = -1
        return 0
    else:
        logger.info("角色授权%s已存在，自动释放资源" % custgroup_name)
        exist_res = vm.get_rec_data_cloud(inner_ip)
        if exist_res == False :
            logger.error("服务器资源%s不存在，没法自动释放资源" % inner_ip)
            rec_code = -1
            role_code = -1
            return 0
        else:
            logger.info("服务器资源%s已存在，可用自动释放资源" % inner_ip)
            add_flag = False
            role_code = vm.update_role_cloud(custgroup_name, vpn_user_name, inner_ip, add_flag)
            #暂不删除资源
            rec_code = 0

    if role_code == 0 and rec_code == 0 :
        msg = "机房%s,vpn用户:%s,释放资源：%s 成功" % (engine_room, vpn_user_name, inner_ip)
        logger.info(msg)
        release_django_VpnInfo(engine_room, vpn_user_name, vpn_phone, inner_ip, custgroup_name)
        res = 1
    else:
        msg = "机房%s,vpn用户:%s,释放资源：%s 失败" % (engine_room, vpn_user_name, inner_ip)
        logger.error(msg)
        send_res = send_mail(msg, msg, 'zhangwei@n-sight.com.cn',
                            settings.Tora_Oper_Group, fail_silently=False)
        ct.send_sms_control('NoLimit', msg, '13681919346')
        res = 0  
    return res


def add_django_VpnInfo(engine_room, vpn_user_name, vpn_phone, inner_ip, custgroup_name, os):
    cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
    admin_user = tmodels.User.objects.filter(username='admin').first()
    vpn_info = get_vpnInfo(engine_room)
    if os[:3].lower() == 'win':
        addr_str = inner_ip + '/3389:3389'
    else:
        addr_str = inner_ip + '/22:22'
    vpn_obj, is_created = tmodels.VpnUserInfo.objects.get_or_create(
                engine_room=engine_room,
                vpn_user_name=vpn_user_name,
                defaults={'vpn_address': vpn_info['vpn_address'],
                          'vpn_user_passwd': vpn_info['vpn_passwd'],
                          'vpn_phone': vpn_phone,
                          'customer': cust_obj,
                          'server_list': addr_str,
                          'operator': admin_user,
                          'cur_status': '1'})
    print("is_created:", is_created)
    if is_created:
        logger.info("增加vpnuser成功")
        return 1
    resource_list = vpn_obj.server_list.split(',')
    if addr_str not in resource_list:
        vpn_obj.server_list += ',' + addr_str
        vpn_obj.save()
        logger.info("更新vpnuser成功")
        return 1
    else:
        logger.info("不需要更新server_list列表")
        return 1

def update_django_VpnInfo(engine_room, vpn_user_name, vpn_phone, addr_strs, note):
    #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
    admin_user = tmodels.User.objects.filter(username='admin').first()
    vpn_info = get_vpnInfo(engine_room)
    # if os[:3].lower() == 'win':
    #     addr_str = inner_ip + '/3389:3389'
    # else:
    #     addr_str = inner_ip + '/22:22'
    if note != '':
        cust_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                        custgroup_name=note,
                        defaults={'phone': vpn_phone,
                                  'email': 'no_mail@n-sight.com.cn',
                                  'operator': admin_user,
                                  'status': '1'})
    else:
        cust_obj = None
    print("cust_objupppp:", cust_obj, engine_room, vpn_user_name,vpn_info,vpn_phone,addr_strs,admin_user)
    vpn_obj, is_created = tmodels.VpnUserInfo.objects.get_or_create(
                engine_room=engine_room,
                vpn_user_name=vpn_user_name,
                defaults={'vpn_address': vpn_info['vpn_address'],
                          'vpn_user_passwd': vpn_info['vpn_passwd'],
                          'vpn_phone': vpn_phone,
                          'server_list': addr_strs,
                          'operator': admin_user,
                          'customer': cust_obj,
                          'cur_status': '1'})
    print("is_createduppp:", is_created)
    if is_created:
        logger.info("增加vpnuser成功")
        return 1
    else:
        logger.info("vpn记录 %s已存在" % vpn_user_name)
        if addr_strs != vpn_obj.server_list:
            vpn_obj.server_list = addr_strs
            vpn_obj.save()
            logger.info("更新vpnuser成功")
            return 1
        else:
            logger.info("不需要更新server_list列表")
            return 1


def release_django_VpnInfo(engine_room, vpn_user_name, vpn_phone, inner_ip, custgroup_name):
    cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
    admin_user = tmodels.User.objects.filter(username='admin').first()
    vpn_info = get_vpnInfo(engine_room)
    vpn_obj, is_created = tmodels.VpnUserInfo.objects.get_or_create(
                engine_room=engine_room,
                vpn_user_name=vpn_user_name,
                defaults={'vpn_address': vpn_info['vpn_address'],
                          'vpn_user_passwd': vpn_info['vpn_passwd'],
                          'vpn_phone': vpn_phone,
                          'customer': cust_obj,
                          'server_list': '',
                          'operator': admin_user,
                          'cur_status': '1'})
    print("is_created:", is_created)
    if is_created:
        logger.info("之前没有记录，增加vpnuser记录成功")
        return 1
    resource_list = vpn_obj.server_list.split(',')
    for res_addr in resource_list:
        server_ip = res_addr.split('/')[0]
        if inner_ip == server_ip:
            resource_list.remove(res_addr)
            vpn_obj.server_list = ','.join(resource_list)
            #列表为空时，不处理状态20210629
            # if len(resource_list) == '0':
            #     vpn_obj.cur_status = '2'
            vpn_obj.save()
            logger.info("更新vpnuser:%s,删除资源%s:成功" % (vpn_user_name,inner_ip))
            return 1
    else:
        logger.info("不需要更新server_list列表")
        return 1


def set_taskflow_fail(id, error_msg):
    task_obj = tmodels.TaskFlow.objects.get(id=id)
    if task_obj.comment != None:
        task_obj.comment += ' error:' + error_msg
    task_obj.comment = error_msg
    task_obj.task_status = '9'
    task_obj.save()


#根据节点分配可用IP
def get_toraCustIP(node_id):
    toraCustIP={'inner_ip':'0.0.0.0',
                'outer_ip':'0.0.0.0',
                'high_trade_ip':'0.0.0.0',
                'high_mqA_ip':'0.0.0.0',
                'high_mqB_ip':'0.0.0.0',
                'other_ip':'0.0.0.0',
                'ipmi_ip':'0.0.0.0'}
    return toraCustIP

def realeaseCustIP(IP):
    #若找到IP置状态为可用，若没有的话增加一条新记录
    logger.info("回收IP：" + str(IP))
    return 1


def get_node_mail_content(node):

    nodeobj = tmodels.NodeInfo.objects.get(pk=node)
    node_no = nodeobj.__getattribute__('node_no')
    content = ''
    nodeConfig = get_nodeConfig(node)
    print("nodeConfig:",nodeConfig)
    business = dict(tmodels.BUSINESS_CHOICES)
    for item_bussi in ['stock','sp','credit']:
        #是否有交易环境
        #print(item_bussi, nodeConfig[item_bussi]['trade']['tradeserver1']['ip_addr'])
        if nodeConfig[item_bussi]['trade']['tradeserver1']['ip_addr'] != '':
            #先写md_L2
            if nodeConfig[item_bussi]['mq']['md_L2']['multicast']['ip_addr'] != '':
                content_stock_md_L2_udp = """【{3}】
                    沪&深L2 组播地址：{4}://{0}:{1}
                    (使用{2}地址段（具体以邮件为准）收取、SourceIP：NULL)
                    #RegisterMulticast("{4}://{0}:{1}","{2}",NULL)
                    """.format(nodeConfig[item_bussi]['mq']['md_L2']['multicast']['ip_addr'], nodeConfig[item_bussi]['mq']['md_L2']['udp']['port'],
                                nodeConfig[item_bussi]['mq']['md_L2']['multicast']['md_rec_addr'],business[item_bussi],
                                nodeConfig[item_bussi]['mq']['md_L2']['multicast']['tele_pattern'])
            else:
                content_stock_md_L2_udp = """【{0}】
                    """.format(business[item_bussi])
            content += content_stock_md_L2_udp
            #剩余其他行情信息和交易信息
            content_stock_second = ''
            if node_no == '4' and item_bussi == 'stock':
                content_stock_second = """
                    L1沪&深行情(MD)交易(TD) FENS的双路地址: tcp://{0}:{1},tcp://{2}:{3}
                    #注册单个fens地址，如：RegisterNameServer("tcp://{0}:{1}")
                    #注册多个fens地址用逗号连接，如：RegisterNameServer("tcp://{0}:{1},tcp://{2}:{3}")（推荐方式）       
                    """.format(nodeConfig[item_bussi]['trade']['fens1']['ip_addr'],nodeConfig[item_bussi]['trade']['fens1']['port'],
                                    nodeConfig[item_bussi]['trade']['fens2']['ip_addr'],nodeConfig[item_bussi]['trade']['fens2']['port'])
                # else:
                #     content_stock_second = """
                #         交易前置(TD)：tcp://{0}:{1}
                #         """.format(nodeConfig[item_bussi]['trade']['trade_front1']['ip_addr'],nodeConfig[item_bussi]['trade']['trade_front1']['port'])
            #非宛平stock节点
            else:
                if nodeConfig[item_bussi]['mq']['sse_md_L2']['multicast']['ip_addr'] != '':
                    content_stock_sse_md_L2 = """
                        沪L2组播行情: {3}://{0}:{1}
                        (使用{2}地址段收取、SourceIP：NULL)
                        """.format(nodeConfig[item_bussi]['mq']['sse_md_L2']['multicast']['ip_addr'],nodeConfig[item_bussi]['mq']['sse_md_L2']['multicast']['port'],
                                    nodeConfig[item_bussi]['mq']['sse_md_L2']['multicast']['md_rec_addr'],nodeConfig[item_bussi]['mq']['sse_md_L2']['multicast']['tele_pattern'])
                    content_stock_second += content_stock_sse_md_L2

                if nodeConfig[item_bussi]['mq']['szse_md_L2B']['multicast']['ip_addr'] != '':
                    content_stock_szse_md_L2B = """
                        深L2 FPGA组播行情：{3}://{0}:{1}
                        (使用{2}地址段收取、SourceIP：NULL)
                        """.format(nodeConfig[item_bussi]['mq']['szse_md_L2B']['multicast']['ip_addr'],nodeConfig[item_bussi]['mq']['szse_md_L2B']['multicast']['port'],
                                    nodeConfig[item_bussi]['mq']['szse_md_L2B']['multicast']['md_rec_addr'],nodeConfig[item_bussi]['mq']['szse_md_L2B']['multicast']['tele_pattern'])
                    content_stock_second += content_stock_szse_md_L2B

                if nodeConfig[item_bussi]['mq']['szse_md_L2A']['multicast']['ip_addr'] != '':
                    content_stock_szse_md_L2A = """
                        深L2 软解组播行情：{3}://{0}:{1}
                        (使用{2}地址段收取、SourceIP：NULL)
                        """.format(nodeConfig[item_bussi]['mq']['szse_md_L2A']['multicast']['ip_addr'],nodeConfig[item_bussi]['mq']['szse_md_L2A']['multicast']['port'],
                                   nodeConfig[item_bussi]['mq']['szse_md_L2A']['multicast']['md_rec_addr'],nodeConfig[item_bussi]['mq']['szse_md_L2A']['multicast']['tele_pattern'])
                    content_stock_second += content_stock_szse_md_L2A

                if nodeConfig[item_bussi]['mq']['md_L2']['tcp']['ip_addr'] != '':
                    content_stock_md_L2_tcp = """
                        沪&深L2 TCP行情：tcp://{0}:{1}
                        """.format(nodeConfig[item_bussi]['mq']['md_L2']['tcp']['ip_addr'],nodeConfig[item_bussi]['mq']['md_L2']['tcp']['port'])
                    content_stock_second += content_stock_md_L2_tcp

                if nodeConfig[item_bussi]['mq']['md_L1']['multicast']['ip_addr'] != '':
                    content_stock_md_L1_udp = """
                        沪&深L1组播行情：{3}://{0}:{1}
                        (使用{2}地址段收取、SourceIP：NULL)
                        """.format(nodeConfig[item_bussi]['mq']['md_L1']['multicast']['ip_addr'],nodeConfig[item_bussi]['mq']['md_L1']['multicast']['port'],
                                    nodeConfig[item_bussi]['mq']['md_L1']['multicast']['md_rec_addr'],nodeConfig[item_bussi]['mq']['md_L1']['multicast']['tele_pattern'])
                    content_stock_second += content_stock_md_L1_udp

                if nodeConfig[item_bussi]['mq']['md_L1']['tcp']['ip_addr'] != '':
                    
                    port_list = (nodeConfig[item_bussi]['mq']['md_L1']['tcp']['port']).split('|')
                    if len(port_list) == 2:
                        content_stock_md_L1_tcp = """
                            沪&深L1 TCP行情：tcp://{0}:{1}
                            (沪深行情合并推送到单一前置，两个端口为互备端口，当一个故障时会自动切换到另一个推送行情，建议同时注册)
                            """.format(nodeConfig[item_bussi]['mq']['md_L1']['tcp']['ip_addr'],nodeConfig[item_bussi]['mq']['md_L1']['tcp']['port'])
                    else:
                        content_stock_md_L1_tcp = """
                        沪&深L1 TCP行情：tcp://{0}:{1}
                        """.format(nodeConfig[item_bussi]['mq']['md_L1']['tcp']['ip_addr'],nodeConfig[item_bussi]['mq']['md_L1']['tcp']['port'])
                    content_stock_second += content_stock_md_L1_tcp

                #if item_bussi == 'stock':
                if node_no != '18':
                    content_stock_trade = """
                        交易主高速A(TD)：tcp://{0}:{1}
                        """.format(nodeConfig[item_bussi]['trade']['tradeserver1']['ip_addr'],nodeConfig[item_bussi]['trade']['tradeserver1']['port'])
                    content_stock_second += content_stock_trade
                    if nodeConfig[item_bussi]['trade']['tradeserver2']['ip_addr'] != '':
                        content_stock_trade2 = """
                            交易备高速A(TD)：tcp://{0}:{1}
                            """.format(nodeConfig[item_bussi]['trade']['tradeserver2']['ip_addr'],nodeConfig[item_bussi]['trade']['tradeserver2']['port'])
                        content_stock_second += content_stock_trade2
                    nodeConfig[item_bussi]['trade']['tradeserver1B']['ip_addr'] = get_another_ip(nodeConfig[item_bussi]['trade']['tradeserver1']['ip_addr'],'inner_ip')
                    if nodeConfig[item_bussi]['trade']['tradeserver1B']['ip_addr'] != '':
                        content_stock_trade1B = """
                            交易主B(TD)：tcp://{0}:{1}
                            """.format(nodeConfig[item_bussi]['trade']['tradeserver1B']['ip_addr'],nodeConfig[item_bussi]['trade']['tradeserver1']['port'])
                        content_stock_second += content_stock_trade1B
                    nodeConfig[item_bussi]['trade']['tradeserver2B']['ip_addr'] = get_another_ip(nodeConfig[item_bussi]['trade']['tradeserver2']['ip_addr'],'inner_ip')
                    if nodeConfig[item_bussi]['trade']['tradeserver2B']['ip_addr'] != '':
                        content_stock_trade2B = """
                            交易备B(TD)：tcp://{0}:{1}
                            """.format(nodeConfig[item_bussi]['trade']['tradeserver2B']['ip_addr'],nodeConfig[item_bussi]['trade']['tradeserver2']['port'])
                        content_stock_second += content_stock_trade2B
                else:
                    content_stock_trade = """交易前置(TD)：tcp://{0}:{1}
                        """.format(nodeConfig[item_bussi]['trade']['trade_front1']['ip_addr'],nodeConfig[item_bussi]['trade']['trade_front1']['port'])
                    content_stock_second += content_stock_trade
                comment_trade = """
                    （备注：主用交易线路A，当A路故障可切换交易线路B）

                    """
                content_stock_second += comment_trade

            content += content_stock_second

    if nodeConfig['cffex']['mq']['cffex_L1']['tcp']['ip_addr'] != '':
        context_cffex = """
            【中金期货】
            中金期货L1行情(MD): tcp://{0}:{1}  
            """.format(nodeConfig['cffex']['mq']['cffex_L1']['tcp']['ip_addr'],nodeConfig['cffex']['mq']['cffex_L1']['tcp']['port'])
        content += context_cffex
    elif nodeConfig['cffex']['mq']['cffex_L1']['multicast']['ip_addr'] != '' :
        context_cffex = """
            【中金期货】
            中金期货L1组播行情(MD): upd://{0}:{1}  
            """.format(nodeConfig['cffex']['mq']['cffex_L1']['multicast']['ip_addr'],nodeConfig['cffex']['mq']['cffex_L1']['multicast']['port'])
        content += context_cffex
    
    return content


class UpgradeThread(Thread):

    def __init__(self, func, args, name=''):
        Thread.__init__(self)
        self.name=name
        #self.func=func
        self.args=args
        self.up_node = upgc.tora_node(*args)
    
    def run(self):
        #python3不支持apply
#        apply(self.func,self.args)
        #self.result = self.up_node.(eval(func))()
        self.result = self.up_node.upgrade_tora()
        
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


@ct.async_run
def nodeUpgrade(taskset):
    error_list=[]
    for task in taskset:
        print('task:', task.id, task.node, task.upgrade_version)
        print("componetValues:", type(task.component), task.component)
        #node_obj = tmodels.NodeInfo.objects.get(pk=)
        print(type(task.node),task.node)
        print(task.node.all())
        node_list = task.node.all()
        # componetList = list(task.component)
        # print(componetList)
        # for item in task.component:
        #     print("item:", type(item), item)
        #print(task.upgrade_node.all())
        #pool = ThreadPool(20)
        #upgrade_res = []

        para_list = []
        for node_item in node_list :
            print("node_item:", node_item.node_no, node_item.node_name)
            para_list.append((node_item.node_no, list(task.component), task.upgrade_version))
            # up_node = upgc.tora_node(node_item.node_id, list(task.component), task.upgrade_version)
            # res = up_node.upgrade_tora() 
            # res = 1
            # logger.info("执行节点%s 升级,返回结果: %s." % (node_item.node_name, str(res)))
            # upgrade_res.append(res)

        thrlist = range(len(node_list))
        res_list=[]
        threads=[]
        for (i, para_item) in zip(thrlist, para_list):
            print("para_item:", i, para_item)
            t = UpgradeThread('upgrade_tora', para_item, 'upgrade_tora' + str(i))
            threads.append(t)
            
        for i in thrlist:
            threads[i].start()
        for i in thrlist:       
            threads[i].join()
            res_list.append(threads[i].get_result())

        total_res = len(res_list) == sum(res_list)
        logger.info(res_list)
        #total_res = 0
        if total_res :
            logger.info("任务%s执行成功" % str(task.id))
            task_obj = tmodels.UpgradeTask.objects.get(id=task.id)
            task_obj.task_status='1'
            task_obj.save()
            
        else:
            logger.error("任务%s执行失败" % str(task.id))
            task_obj = tmodels.UpgradeTask.objects.get(id=task.id)
            task_obj.task_status='4'
            task_obj.save()
            error_list.append(task)

@ct.async_run
def nodeRestore(taskset):
    for task in taskset:
        print('task:', task.id, task.node, task.upgrade_version)


def gen_node_cfg_module(queryset):
    for node in queryset:
        print('node:', node.node_no)
        content = get_node_mail_content(node.id)
        node.node_cfg_module = content.replace('    ','')
        node.save()
    return 1


def get_node_cfg_module(node_no):
    nodeobj = tmodels.NodeInfo.objects.filter(node_no=node_no).first()
    mail_module = nodeobj.node_cfg_module
    if mail_module == '':
        content = get_node_mail_content(nodeobj.id)
        mail_module = content.replace('    ','')
        nodeobj.node_cfg_module = mail_module
        nodeobj.save()

    return mail_module
    


#取所有的choices配置
def get_choices():
    config_path = os.path.join(settings.BASE_DIR, "config")
    choices_file = os.path.join(config_path,'form_choices.json')
    #print(choices_file)
    with open(choices_file, 'r', encoding='UTF-8') as f:
        Jsondata = json.load(f)
        #print(type(Jsondata), Jsondata) 
    return Jsondata

def get_choices2():
    config_path = os.path.join(settings.BASE_DIR, "config")
    choices_file = os.path.join(config_path,'form_choices.json')
    #print(choices_file)
    with open(choices_file, 'r', encoding='UTF-8') as f:
        Jsondata = json.load(f)
        #print(type(Jsondata), Jsondata) 
    return Jsondata



def dict2tuple(dictData):
    temp_list = []
    for key in dictData:
        temp_list.append((key,dictData[key]))
    #print(temp_list)
    return tuple(temp_list)


'''执行django原始sql语句  并返回一个list对象'''
def executeOriginalsql(sql):
        logger.info('excutesql:')
        logger.info(sql)
        cursor = connection.cursor()  # 获得一个游标(cursor)对象
        cursor.execute(sql)
        rawData = cursor.fetchall()
        print(rawData)
        col_names = [desc[0] for desc in cursor.description]
        #print(col_names)

        result = []
        for row in rawData:
            objDict = {}
            # 把每一行的数据遍历出来放到Dict中
            for index, value in enumerate(row):
                #print(index, col_names[index], value)
                objDict[col_names[index]] = value

            result.append(objDict)
        return result


def get_min_assigned_server(match_server):
    df = pd.DataFrame(match_server)
    print(df)
    return (df['inner_ip'][df['assigned_count'] == df['assigned_count'].min()].values[0])


def choice_share_server(engine_room, os, os_version, node_no):
    #查询可用服务器
    #s = tmodels.ShareServerInfo.objects.filter(Q(engine_room='dgnf') & Q(machine__node__node_no='7'))
    #s = tmodels.ShareServerInfo.objects.filter(machine__node__node_no='7')
    #share_type='2'，客户共用
    serverSet = tmodels.ShareServerInfo.objects.filter(Q(machine__node__node_no=node_no), 
                                                       Q(share_type='2'),
                                                       Q(is_active='1'),
                                                       Q(machine__os='redhat') | Q(machine__os='centos') | Q(machine__os='ubuntu'))

    if len(serverSet) == 0:
        logger.info("该节点没有linux共有服务器")
        inner_ip = None
    else:
        match_server=[]
        for server in serverSet:
            dict_data = {}   
            dict_data['inner_ip'] = server.machine__inner_ip
            dict_data['os'] = server.machine__os
            dict_data['os_version'] = server.machine__os_version
            dict_data['assigned_count'] = server.assigned_count
            match_server.append(dict_data)
        ubuntu_server = []
        full_match_server = []
        os_match_server = []
        linux_match_server = []
        for server_dict in match_server:
            if server_dict['os'] == os and server_dict['os_version'] == os_version:
                full_match_server.append(server_dict)
            elif server_dict['os'] == os:
                os_match_server.append(server_dict)
            else:
                logger.info("系统不匹配的linux服务器！")
                linux_match_server.append(server_dict)

        if os != 'ubuntu':
            if len(full_match_server) != 0 :
                inner_ip = get_min_assigned_server(full_match_server)    
            elif len(os_match_server) != 0 :
                logger.info("版本不对任选一个")
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
                logger.info("版本不对任选一个")
                inner_ip = get_min_assigned_server(os_match_server)
            else:
                logger.info("系统不匹配的ubuntu不做自动选择")
                inner_ip = None
    return inner_ip
            


def copy_ssh_rsa(serverSet):
    
    user_para = tmodels.GloblePara.objects.get(para_name='rsa_user')
    username = user_para.para_value
    passwd_para = tmodels.GloblePara.objects.get(para_name='rsa_passwd')
    password = passwd_para.para_value
    error_ip = []
    for server in serverSet:
        hostip = server.inner_ip
        old_rsa_user = server.rsa_users
        command = './common/copy_ssh_rsa.sh %s %s %s' % (hostip, username, password)
        logger.info(command)
        try:
            res = subprocess.run(command,shell=True,check=True,capture_output=True)
            if res.returncode == 0:
                logger.info("success:" + str(res))
                if old_rsa_user != None:
                    server.rsa_users = old_rsa_user + ',' + username
                else:
                    server.rsa_users = username
                server.save()
                #加入ip到hosts文件
                hosts_file = '/etc/ansible/hosts'
                w_command = "echo %s >> %s" % (hostip, hosts_file)
                #print("w_command:",w_command)
                os.system(w_command)
            else:
                logger.error("error:" + str(res))
            logger.info("res.returncode:" + str(res.returncode))
            logger.info("res.stdout:" + res.stdout.decode('utf-8'))
            res_error = res.stderr.decode('utf-8')
            logger.error("res_error:" + res_error)

        except Exception as e:
            res_error = "copy_ssh_rsa 执行异常!" + str(e)
            logger.error("res_error11:" + res_error)

        if res_error:
            logger.error(res_error)
            msg = "Error,服务器[%s]copy_ssh_rsa异常，错误消息：[%s]" % (hostip,res_error)
            logger.error(msg)
            error_ip.append(hostip)
            #ct.send_sms_control('NoLimit', msg)
        else:
            # check_list.append(1)
            msg = "Ok,服务器[%s] copy_ssh_rsa 成功" % hostip
            logger.info(msg)
    if len(error_ip) != 0:
        msg = "执行免密出现错误的IP：" + ','.join(error_ip)
        logger.error(msg)
        return {'code':0, 'data': error_ip}
    else:
        return {'code':1, 'data':'success'}


def get_cust_phone_by_ip(hostip):
    #hostip = '192.168.10.214'
    try:
        machine_obj = tmodels.ShelfMachine.objects.get(inner_ip=hostip)
        # machine_owner = machine_obj.owner
        # cust_obj = tmodels.ToraCustomer.objects.get(id=machine_owner.id)
        # cust_phone = cust_obj.phone
        use_customers = machine_obj.customer.all()
        phone_list = []
        for cust in use_customers:
            if cust.phone not in ['no_phone','0','']:
                phone_list.append(cust.phone)
        cust_phone = ','.join(phone_list)

    except Exception as e:
        msg = "服务器%s, 取客户手机号码出现异常!" % hostip
        logger.error(msg)
        cust_phone = None
    return cust_phone


def get_phone_by_custgroup_name(custgroup_name='全创运行组'):

    try:
        opm_obj = tmodels.ToraCustomer.objects.get(custgroup_name=custgroup_name)
        opm_phone = opm_obj.phone
    except Exception as e:
        msg = "取运维组手机号码出现异常!" 
        logger.error(msg)
        opm_phone = None
    return opm_phone


def send_cust_error_sms(hostip, msg):
    cust_phone = get_cust_phone_by_ip(hostip)
    #opm_phone = get_opm_phone()
    opm_phone = get_phone_by_custgroup_name('全创运行组')
    print("cust_phone:", cust_phone)
    if len(cust_phone) < 11 or cust_phone in [None,'']:
        msg2 = '客户没有手机号_' + msg
        logger.error(msg2)
        #ct.send_sms_control('NoLimit', msg2, opm_phone)
        send_monitor_sms('NoLimit', msg2, opm_phone)
    else:
        send_phone = cust_phone + ',' + opm_phone
        #print("send_phone:", send_phone)
        logger.error(msg)
        #ct.send_sms_control('NoLimit', msg, send_phone)
        send_monitor_sms('NoLimit', msg, send_phone)


#导入独用的客户服务器信息
@ct.async_run
def import_cust_machine():
    pddata = pd.read_csv('./config/cust_machine_20210910.csv', encoding='gbk', keep_default_na=False)
    #如果有过滤参数'is_monitor'，则过滤需要监控的记录
    pd_columns = pddata.columns.values.tolist()
    #print("pdata:", pddata)
    for row in pddata.itertuples():
        # node_name = getattr(row, 'node_name')
        # opertaion_system = getattr(row, 'opertaion_system')
        # disk_serial = getattr(row, 'disk_serial_number')
        # vpns = getattr(row, 'vpn')
        # vpn_list = vpns.split(';')
        engine_room = getattr(row, 'engine_room')
        assert_number = getattr(row, 'assert_number')
        assert_type_str = getattr(row, 'assert_type')
        room_no = getattr(row, 'room_no')
        row_no = getattr(row, 'row_no')
        cabinet = getattr(row, 'cabinet')
        unit = getattr(row, 'unit')
        model = getattr(row, 'model')
        serial_number = getattr(row, 'serial_number')
        IT_checked_number = getattr(row, 'IT_checked_number')
        #configuration = getattr(row, 'configuration')
        node_name = getattr(row, 'node_name')
        #use_status = getattr(row, 'use_status')
        opertaion_system = getattr(row, 'opertaion_system')
        inner_ip = getattr(row, 'inner_ip')
        outer_ip = getattr(row, 'outer_ip')
        high_trade_ip = getattr(row, 'high_trade_ip')
        high_mqA_ip = getattr(row, 'high_mqA_ip')
        high_mqB_ip = getattr(row, 'high_mqB_ip')
        ipmi_ip = getattr(row, 'ipmi_ip')
        #note = getattr(row, 'note')
        disk_serial = getattr(row, 'disk_serial_number')
        custgroup_name = getattr(row, 'custgroup_name')
        shelf_date = getattr(row, 'shelf_date')
        buyer = getattr(row, 'buyer')
        comment = getattr(row, 'comment')


        if engine_room == '金桥机房':
            engine_room = 'shjq'
        elif engine_room == '南方中心机房':
            engine_room = 'dgnf'
        elif engine_room == '技术大厦机房':
            engine_room = 'shgq'
        elif engine_room == '宛平机房':
            engine_room = 'shwp'

        if inner_ip == '':
            inner_ip = '0.0.0.0'

        if assert_type_str == '虚拟机':
            assert_type = '2'
        elif assert_type_str == '云服务器':
            assert_type = '3'
        elif assert_type_str == '交换机':
            assert_type = '4'
        elif assert_type_str == '超级光分器':
            assert_type = '5'
        elif assert_type_str == '进线设备':
            assert_type = '9'
        else:
            assert_type = '1'

        #print("test:::",model, model=='')
        if model:
            band_models = model.split()
            server_brand = band_models[0].capitalize()
            server_model = model
        else:
            server_brand = 'None'
            server_model = 'None'

        if not serial_number :
            serial_number = 'None'

        if cabinet == '虚拟机' or cabinet == '' :
            cabinet = 'None'

        if not unit :
            unit = 'None'

        if not IT_checked_number :
            IT_checked_number = 'None'

        os ='no_os'
        os_version = 'no_version'
        for os_item in ['redhat','centos','ubuntu','windows','clear linux','clearos','gentoo','arch linux','debian']:
            i = len(os_item)
            #print(i, opertaion_system[:6].lower())
            if opertaion_system[:i].lower() == os_item:
                os = os_item
                os_version = opertaion_system[i:].strip()          
                continue
        
        if os == 'no_os':
            os = opertaion_system
            if os == '':
                os = 'not sure'
        #print(os, os_version)
        #print(custgroup_name, buyer)
        #print(shelf_time,node_name)
        node_no = node_name.split('号节点')[0]
        #print("node_no:", node_no, type(node_no))
        if node_no:
            nodeobj = tmodels.NodeInfo.objects.filter(node_no=node_no).first()
        else:
            nodeobj, is_created = tmodels.NodeInfo.objects.get_or_create(
                                node_no='00',
                                defaults={'engine_room': engine_room,
                                'node_name': engine_room + '_空节点'})
    
        print(inner_ip, shelf_date)
        if shelf_date in ['空','还不确定','待确认','']:
            shelf_date = '2010-01-01'
        else:
            #shelf_date = time.mktime(time.strptime(shelf_time, "%Y年%M月%d日"))
            date_str = shelf_date.replace('年','-').replace('月','-').replace('日','')
            date_list = date_str.split('-')
            print("date_str:",date_str)
            if len(date_list[1]) == 1:
                mm = '0' + date_list[1]
            else:
                mm = date_list[1]
            if len(date_list[2]) == 1:
                dd = '0' + date_list[2]
            else:
                dd = date_list[2]
            shelf_date = '%s-%s-%s' % (date_list[0], mm, dd)
        #print(shelf_date)
        #print(use_status, buyer)
        admin_user = tmodels.User.objects.filter(username='admin').first()
        #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
        cust_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                custgroup_name=custgroup_name,
                defaults={'phone': 'no_phone',
                            'email': 'no_mail@n-sight.com.cn',
                            'operator': admin_user,
                            'status': '1'})
        if buyer == '客户自购':
            #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
            owner_obj = cust_obj
        elif buyer in ['华鑫采购','华鑫自有']:
            #hxzq_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='华鑫证券').first()
            hxzq_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name=buyer,
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
            owner_obj = hxzq_obj
        elif buyer == 'N-Sight':
            #hxzq_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='华鑫证券').first()
            hxzq_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name='全创科技',
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
            owner_obj = hxzq_obj
        else:
            #qckj_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='全创科技').first()
            qckj_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name='其他',
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
            owner_obj = qckj_obj
        purpose = '1'
 
        #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
        #owner_obj = cust_obj
        machine_obj, is_created = tmodels.ShelfMachine.objects.get_or_create(
                        engine_room=engine_room,
                        inner_ip=inner_ip,
                        serial_number=serial_number,
                        defaults={'engine_room': engine_room,
                                'assert_number': assert_number,
                                'assert_type': assert_type,
                                'room_no': room_no,
                                'row_no': row_no,
                                'cabinet': cabinet,
                                'unit': unit,
                                'node': nodeobj,
                                'owner': owner_obj,
                                'purpose': purpose,
                                'server_brand': server_brand,
                                'server_model': server_model,
                                'IT_checked_number': IT_checked_number,
                                'disk_serial': disk_serial,
                                'outer_ip': outer_ip,
                                'high_trade_ip': high_trade_ip,
                                'high_mqA_ip': high_mqA_ip,
                                'high_mqB_ip': high_mqB_ip,
                                'ipmi_ip': ipmi_ip,
                                'shelf_date': shelf_date,
                                'comment': comment,
                                'operator': admin_user})
        print("is_created:", is_created)
        #'customer': cust_obj
        if custgroup_name:
            cust_set =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name)
            machine_obj.customer.set(cust_set)

#导入独用的客户服务器信息
@ct.async_run
def import_cust_share_machine():
    purpose = '2' #客户共用
    pddata = pd.read_csv('./config/cust_share_server_0913.csv', encoding='gbk', keep_default_na=False)
    #如果有过滤参数'is_monitor'，则过滤需要监控的记录
    pd_columns = pddata.columns.values.tolist()
    #print("pdata:", pddata)
    for row in pddata.itertuples():
        # node_name = getattr(row, 'node_name')
        # opertaion_system = getattr(row, 'opertaion_system')
        # disk_serial = getattr(row, 'disk_serial_number')
        # vpns = getattr(row, 'vpn')
        # vpn_list = vpns.split(';')
        engine_room = getattr(row, 'engine_room')
        assert_number = getattr(row, 'assert_number')
        assert_type_str = getattr(row, 'assert_type')
        room_no = getattr(row, 'room_no')
        row_no = getattr(row, 'row_no')
        cabinet = getattr(row, 'cabinet')
        unit = getattr(row, 'unit')
        model = getattr(row, 'model')
        serial_number = getattr(row, 'serial_number')
        IT_checked_number = getattr(row, 'IT_checked_number')
        #configuration = getattr(row, 'configuration')
        node_name = getattr(row, 'node_name')
        #use_status = getattr(row, 'use_status')
        opertaion_system = getattr(row, 'opertaion_system')
        inner_ip = getattr(row, 'inner_ip')
        outer_ip = getattr(row, 'outer_ip')
        high_trade_ip = getattr(row, 'high_trade_ip')
        high_mqA_ip = getattr(row, 'high_mqA_ip')
        high_mqB_ip = getattr(row, 'high_mqB_ip')
        ipmi_ip = getattr(row, 'ipmi_ip')
        #note = getattr(row, 'note')
        disk_serial = getattr(row, 'disk_serial_number')
        custgroup_name = getattr(row, 'custgroup_name')
        shelf_date = getattr(row, 'shelf_date')
        buyer = getattr(row, 'buyer')
        comment = getattr(row, 'comment')


        if engine_room == '金桥机房':
            engine_room = 'shjq'
        elif engine_room == '南方中心机房':
            engine_room = 'dgnf'
        elif engine_room == '技术大厦机房':
            engine_room = 'shgq'
        elif engine_room == '宛平机房':
            engine_room = 'shwp'

        if inner_ip == '':
            inner_ip = '0.0.0.0'

        if assert_type_str == '虚拟机':
            assert_type = '2'
        elif assert_type_str == '云服务器':
            assert_type = '3'
        elif assert_type_str == '交换机':
            assert_type = '4'
        elif assert_type_str == '超级光分器':
            assert_type = '5'
        elif assert_type_str == '进线设备':
            assert_type = '9'
        else:
            assert_type = '1'

        #print("test:::",model, model=='')
        if model:
            band_models = model.split()
            server_brand = band_models[0].capitalize()
            server_model = model
        else:
            server_brand = 'None'
            server_model = 'None'

        if not serial_number :
            serial_number = 'None'

        if cabinet == '虚拟机' or cabinet == '' :
            cabinet = 'None'

        if not unit :
            unit = 'None'

        if not IT_checked_number :
            IT_checked_number = 'None'

        os ='no_os'
        os_version = 'no_version'
        for os_item in ['redhat','centos','ubuntu','windows','clear linux','clearos','gentoo','arch linux','debian']:
            i = len(os_item)
            #print(i, opertaion_system[:6].lower())
            if opertaion_system[:i].lower() == os_item:
                os = os_item
                os_version = opertaion_system[i:].strip()          
                continue
        
        if os == 'no_os':
            os = opertaion_system
            if os == '':
                os = 'not sure'
        #print(os, os_version)
        #print(custgroup_name, buyer)
        #print(shelf_time,node_name)
        node_no = node_name.split('号节点')[0]
        #print("node_no:", node_no, type(node_no))
        if node_no:
            nodeobj = tmodels.NodeInfo.objects.filter(node_no=node_no).first()
        else:
            nodeobj, is_created = tmodels.NodeInfo.objects.get_or_create(
                                node_no='00',
                                defaults={'engine_room': engine_room,
                                'node_name': engine_room + '_空节点'})
        if shelf_date in ['空','还不确定','待确认','']:
            shelf_date = '2010-01-01'
        else:
            #shelf_date = time.mktime(time.strptime(shelf_time, "%Y年%M月%d日"))
            date_str = shelf_date.replace('年','-').replace('月','-').replace('日','')
            date_list = date_str.split('-')
            print("date_str:",date_str)
            if len(date_list[1]) == 1:
                mm = '0' + date_list[1]
            else:
                mm = date_list[1]
            if len(date_list[2]) == 1:
                dd = '0' + date_list[2]
            else:
                dd = date_list[2]
            shelf_date = '%s-%s-%s' % (date_list[0], mm, dd)
        #print(shelf_date)
        #print(use_status, buyer)
        admin_user = tmodels.User.objects.filter(username='admin').first()
        #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
        if custgroup_name:
            group_name_list = custgroup_name.split(";")

            for group_name in group_name_list:
                cust_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                        custgroup_name=group_name,
                        defaults={'phone': 'no_phone',
                                    'email': 'no_mail@n-sight.com.cn',
                                    'operator': admin_user,
                                    'status': '1'})
            
            #cust_set.append[cust_obj]
        # if buyer == '客户自购':
        #     #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
        #     owner_obj = cust_obj
        if buyer in ['华鑫采购','华鑫自有']:
            #hxzq_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='华鑫证券').first()
            hxzq_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name=buyer,
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
            owner_obj = hxzq_obj
        elif buyer == 'N-Sight':
            #hxzq_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='华鑫证券').first()
            hxzq_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name='全创科技',
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
            owner_obj = hxzq_obj
        else:
            #qckj_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='全创科技').first()
            qckj_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name='其他',
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
            owner_obj = qckj_obj
        
 
        #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
        #owner_obj = cust_obj
        machine_obj, is_created = tmodels.ShelfMachine.objects.get_or_create(
                        engine_room=engine_room,
                        inner_ip=inner_ip,
                        serial_number=serial_number,
                        defaults={'engine_room': engine_room,
                                'assert_number': assert_number,
                                'assert_type': assert_type,
                                'room_no': room_no,
                                'row_no': row_no,
                                'cabinet': cabinet,
                                'unit': unit,
                                'node': nodeobj,
                                'owner': owner_obj,
                                'purpose': purpose,
                                'server_brand': server_brand,
                                'server_model': server_model,
                                'IT_checked_number': IT_checked_number,
                                'disk_serial': disk_serial,
                                'outer_ip': outer_ip,
                                'high_trade_ip': high_trade_ip,
                                'high_mqA_ip': high_mqA_ip,
                                'high_mqB_ip': high_mqB_ip,
                                'ipmi_ip': ipmi_ip,
                                'shelf_date': shelf_date,
                                'comment': comment,
                                'operator': admin_user})
        print("is_created:", is_created)
        #'customer': cust_obj
        if custgroup_name:
            cust_ids = []
            for group_name in group_name_list:
                cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=group_name).first()
                machine_obj.customer.add(cust_obj.id)
                cust_ids.append(cust_obj.id)
            #machine_obj.customer.set(cust_ids)


#导入奇点服务器信息
@ct.async_run
def import_tora_machine():
    purpose = '3' #华鑫奇点自用
    pddata = pd.read_csv('./config/tora_server_20210914.csv', encoding='gbk', keep_default_na=False)
    #如果有过滤参数'is_monitor'，则过滤需要监控的记录
    pd_columns = pddata.columns.values.tolist()
    #print("pdata:", pddata)
    for row in pddata.itertuples():
        # node_name = getattr(row, 'node_name')
        # opertaion_system = getattr(row, 'opertaion_system')
        # disk_serial = getattr(row, 'disk_serial_number')
        # vpns = getattr(row, 'vpn')
        # vpn_list = vpns.split(';')
        engine_room = getattr(row, 'engine_room')
        assert_number = getattr(row, 'assert_number')
        assert_type_str = getattr(row, 'assert_type')
        room_no = getattr(row, 'room_no')
        row_no = getattr(row, 'row_no')
        cabinet = getattr(row, 'cabinet')
        unit = getattr(row, 'unit')
        model = getattr(row, 'model')
        serial_number = getattr(row, 'serial_number')
        IT_checked_number = getattr(row, 'IT_checked_number')
        #configuration = getattr(row, 'configuration')
        node_name = getattr(row, 'node_name')
        #use_status = getattr(row, 'use_status')
        opertaion_system = getattr(row, 'opertaion_system')
        inner_ip = getattr(row, 'inner_ip')
        outer_ip = getattr(row, 'outer_ip')
        high_trade_ip = getattr(row, 'high_trade_ip')
        high_mqA_ip = getattr(row, 'high_mqA_ip')
        high_mqB_ip = getattr(row, 'high_mqB_ip')
        ipmi_ip = getattr(row, 'ipmi_ip')
        #note = getattr(row, 'note')
        #disk_serial = getattr(row, 'disk_serial_number')
        custgroup_name = getattr(row, 'custgroup_name')
        shelf_date = getattr(row, 'shelf_date')
        #buyer = getattr(row, 'buyer')
        comment = getattr(row, 'comment')


        if engine_room == '金桥机房':
            engine_room = 'shjq'
        elif engine_room == '南方中心机房':
            engine_room = 'dgnf'
        elif engine_room == '技术大厦机房':
            engine_room = 'shgq'
        elif engine_room == '宛平机房':
            engine_room = 'shwp'
        elif engine_room == '科技网':
            engine_room = 'shkj'
        elif engine_room == '斜土路机房':
            engine_room = 'shxt'

        if inner_ip == '':
            inner_ip = '0.0.0.0'

        if assert_type_str == '虚拟机':
            assert_type = '2'
        elif assert_type_str == '云服务器':
            assert_type = '3'
        elif assert_type_str == '交换机':
            assert_type = '4'
        elif assert_type_str == '超级光分器':
            assert_type = '5'
        elif assert_type_str == '进线设备':
            assert_type = '9'
        else:
            assert_type = '1'

        #print("test:::",model, model=='')
        if model:
            band_models = model.split()
            server_brand = band_models[0].capitalize()
            server_model = model
        else:
            server_brand = 'None'
            server_model = 'None'

        if server_brand.lower() == 'n-sight':
            buyer = 'N-Sight'
        else:
            buyer = '华鑫自有'

        if not serial_number :
            serial_number = 'None'

        if cabinet == '虚拟机' or cabinet == '' :
            cabinet = 'None'

        if not unit :
            unit = 'None'

        if not IT_checked_number :
            IT_checked_number = 'None'

        os ='no_os'
        os_version = 'no_version'
        for os_item in ['redhat','centos','ubuntu','windows','clear linux','clearos','gentoo','arch linux','debian']:
            i = len(os_item)
            #print(i, opertaion_system[:6].lower())
            if opertaion_system[:i].lower() == os_item:
                os = os_item
                os_version = opertaion_system[i:].strip()          
                continue
        
        if os == 'no_os':
            os = opertaion_system
            if os == '':
                os = 'not sure'
        #print(os, os_version)
        #print(custgroup_name, buyer)
        #print(shelf_time,node_name)
        if node_name:
            name_list = node_name.split(';')
            #取第一个节点值
            busniess = name_list[0].split('-')[0]
            node_no = name_list[0].split('-')[1]
            #print("node_no:", node_no, type(node_no))
        else:
            node_no = None
        if node_no:
            nodeobj = tmodels.NodeInfo.objects.filter(node_no=node_no).first()
        else:
            nodeobj, is_created = tmodels.NodeInfo.objects.get_or_create(
                                node_no='00',
                                defaults={'engine_room': engine_room,
                                'node_name': engine_room + '_空节点'})
        if shelf_date in ['空','还不确定','待确认','']:
            shelf_date = '2010-01-01'
        else:
            #shelf_date = time.mktime(time.strptime(shelf_time, "%Y年%M月%d日"))
            date_str = shelf_date.replace('年','-').replace('月','-').replace('日','')
            date_list = date_str.split('-')
            print("date_str:",date_str)
            if len(date_list[1]) == 1:
                mm = '0' + date_list[1]
            else:
                mm = date_list[1]
            if len(date_list[2]) == 1:
                dd = '0' + date_list[2]
            else:
                dd = date_list[2]
            shelf_date = '%s-%s-%s' % (date_list[0], mm, dd)
        #print(shelf_date)
        #print(use_status, buyer)
        admin_user = tmodels.User.objects.filter(username='admin').first()
        if custgroup_name:
            cust_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name=custgroup_name,
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
                
        if buyer in ['华鑫采购','华鑫自有']:
            #hxzq_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='华鑫证券').first()
            hxzq_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name=buyer,
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
            owner_obj = hxzq_obj
        elif buyer == 'N-Sight':
            #hxzq_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='华鑫证券').first()
            hxzq_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name='全创科技',
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
            owner_obj = hxzq_obj
        else:
            #qckj_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='全创科技').first()
            qckj_obj, is_cust_created = tmodels.ToraCustomer.objects.get_or_create(
                    custgroup_name='其他',
                    defaults={'phone': 'no_phone',
                                'email': 'no_mail@n-sight.com.cn',
                                'operator': admin_user,
                                'status': '1'})
            owner_obj = qckj_obj
        
 
        #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
        #owner_obj = cust_obj
        machine_obj, is_created = tmodels.ShelfMachine.objects.get_or_create(
                        engine_room=engine_room,
                        inner_ip=inner_ip,
                        serial_number=serial_number,
                        defaults={'engine_room': engine_room,
                                'assert_number': assert_number,
                                'assert_type': assert_type,
                                'room_no': room_no,
                                'row_no': row_no,
                                'cabinet': cabinet,
                                'unit': unit,
                                'node': nodeobj,
                                'owner': owner_obj,
                                'purpose': purpose,
                                'server_brand': server_brand,
                                'server_model': server_model,
                                'IT_checked_number': IT_checked_number,
                                'outer_ip': outer_ip,
                                'high_trade_ip': high_trade_ip,
                                'high_mqA_ip': high_mqA_ip,
                                'high_mqB_ip': high_mqB_ip,
                                'ipmi_ip': ipmi_ip,
                                'shelf_date': shelf_date,
                                'comment': comment,
                                'operator': admin_user})
        print("is_created:", is_created, inner_ip,serial_number)
        #'customer': cust_obj
        if custgroup_name:
            #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
            #machine_obj.customer.add(cust_obj.id)
            cust_set =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name)
            machine_obj.customer.set(cust_set)


@ct.async_run
def import_node_trade_info():

    csvfile_path = './config/node_trade_info_20210914.csv' 
    pddata = pd.read_csv(csvfile_path, encoding='gbk', keep_default_na=False)
    admin_user = tmodels.User.objects.filter(username='admin').first()
    #增加节点信息
    node_set = set(pddata['node_no'])
    for no in node_set:
        piece = pddata.loc[(pddata['node_no'] == no) & (pddata['app_type'] == 'tradeserver1')]
        #print(no, list(piece['business']))
        engine_room = list(piece['engine_room'])[0]
        if engine_room == 'dgnf':
            prex = '东莞'
        elif engine_room == 'shjq':
            prex = '金桥'
        elif engine_room == 'shgq':
            prex = '外高桥'
        elif engine_room == 'shwp':
            prex = '宛平'
        else:
            prex = '其他'
        node_name = prex + str(no) + '号'
        node_obj, is_created = tmodels.NodeInfo.objects.get_or_create(
                                node_no=str(no),
                                defaults={'node_name': node_name,
                                        'business': list(piece['business']),
                                        'engine_room': engine_room})

    #增加节点服务信息
    for row in pddata.itertuples():
        engine_room = getattr(row, 'engine_room')
        node_no = getattr(row, 'node_no')
        business = getattr(row, 'business')
        app_type = getattr(row, 'app_type')
        ip_addr = getattr(row, 'ip_addr')
        port = getattr(row, 'port')
        internet_addr_ports = getattr(row, 'internet_addr_ports')
        current_version = getattr(row, 'current_version')
        #internet_port = getattr(row, 'internet_port')

        nodeobj = tmodels.NodeInfo.objects.filter(node_no=node_no).first()
        print(nodeobj,business,internet_addr_ports)
        tradenode_obj, is_created = tmodels.TradeNode.objects.get_or_create(
                                node=nodeobj,
                                business=business,
                                app_type=app_type,
                                defaults={'ip_addr': ip_addr,
                                        'port': port,
                                        'internet_addr_ports': internet_addr_ports})
        #增加版本号
        if app_type == 'tradeserver1':

            nodedetail_obj, is_created = tmodels.NodeDetailInfo.objects.get_or_create(
                                    node=nodeobj,
                                    business=business,
                                    defaults={'current_version': current_version,
                                            'operator': admin_user})
            if not is_created:
                #print("修改节点信息",nodeobj,current_version)
                nodedetail_obj.current_version = current_version
                nodedetail_obj.save()
                #print("修改后节点信息",nodeobj,business,current_version)
    #增加行情配置信息
    mqcfg_path = './config/mq_node_info_20210908.csv' 
    pdmq = pd.read_csv(mqcfg_path, encoding='gbk', keep_default_na=False)
    for row in pdmq.itertuples():
        node_nos = getattr(row, 'node_nos')
        #mq_group_name = getattr(row, 'mq_group_name')
        business = getattr(row, 'business')
        mq_type = getattr(row, 'mq_type')
        register_type = getattr(row, 'register_type')
        tele_pattern = getattr(row, 'tele_pattern')
        ip_addr = getattr(row, 'ip_addr')
        port = getattr(row, 'port')
        md_rec_addr = getattr(row, 'md_rec_addr')
        source_ip = getattr(row, 'source_ip')


        # mqgroup_obj, is_created = tmodels.ToraMqGroup.objects.get_or_create(
        #                         mq_group_name=mq_group_name,
        #                         engine_room=mq_group_name[:4])

        nodeobj = tmodels.NodeInfo.objects.filter(node_no=node_no).first()

        mq_obj, is_created = tmodels.ToraMq.objects.get_or_create(
                                node_nos=node_nos,
                                business=business.split(";"),
                                mq_type=mq_type,
                                register_type=register_type,
                                defaults={'tele_pattern': tele_pattern,
                                        'ip_addr': ip_addr,
                                        'port': port,
                                        'md_rec_addr': md_rec_addr,
                                        'source_ip': source_ip})
    #增加版本号


#根据一个IP来获取机器的别的IP地址
def get_another_ip(ip_addr, ip_type='inner_ip'):
    # for ip_filed in ['inner_ip','outer_ip','high_trade_ip','high_mqA_ip','high_mqB_ip','ipmi_ip','other_ip']:
    #     machine_obj = tmodels.ShelfMachine.objects.filter(ip_filed)
    machine_obj = tmodels.ShelfMachine.objects.filter(Q(inner_ip=ip_addr) | Q(outer_ip=ip_addr)\
                                                     | Q(high_trade_ip=ip_addr) | Q(high_mqA_ip=ip_addr)\
                                                     | Q(high_mqB_ip=ip_addr) | Q(ipmi_ip=ip_addr)).first()
    if machine_obj and (ip_type in ['inner_ip','outer_ip','high_trade_ip','high_mqA_ip','high_mqB_ip','ipmi_ip','other_ip']):
        return machine_obj.__getattribute__(ip_type)
    else:
        return None


'''
启动程序时清理一下短信控制表，防止程序出错发爆短信，根据日期每天执行一次
'''
def get_sms_control_data():
    from myapps.tora_monitor import models as mmodels
    today = dt.datetime.now().strftime("%Y-%m-%d")
    sms_cfg_obj, is_created = mmodels.SmsControlData.objects.get_or_create(
                init_day=today,
                defaults={'ps_port': 0,
                          'disk': 0,
                          'mem': 0,
                          'ping': 0,
                          'db_trade': 0,
                          'core': 0,
                          'errorID': 0,
                          'errorlog': 0,
                          'ipmi': 0,
                          'NoLimit': 0,
                          'total_used_count': 0,
                          'single_limit': 20,
                          'total_limit': 500})
    if is_created:
        logger.info("初始化sms_control成功！")
    else:
        logger.info("sms_control当日已经初始化！")

    return sms_cfg_obj

'''
短信发送控制，总短信数控制，和单项监控短信控制
'''
def send_monitor_sms(sms_type, msg, phone='13162583883,13681919346,13816703919,18917952875,17512562551,13651808091'):
    
    try:
        # countfile = './config/trade_monitor_para.json'
        # with open(countfile, 'r') as f:
        #     Json_dic = json.load(f)
        #     logger.debug(Json_dic)
        sms_cfg_obj = get_sms_control_data()

        total_used_count = sms_cfg_obj.total_used_count
        single_limit = sms_cfg_obj.single_limit
        total_count = sms_cfg_obj.total_limit
        print("total_count:", total_count)
    except Exception as e:
        print("发送异常")
        print(str(e))
    try:
        single_times = getattr(sms_cfg_obj,sms_type)
    except Exception as e:
        logger.warning(str(e))
        single_times = 9999    
    if sms_type == "NoLimit":
        #NoLimit不限制
        single_times = 0
    logger.info("单项已发送短信次数：%d" % single_times)
    logger.info("已发送短信总条数：%d" % total_used_count)
    #小于限制时才允许发送短信
    if single_times != 9999 and total_used_count < total_count and single_times < single_limit:
        message = "【奇点监控】" + msg
        ct.fortunesms(message, phone)
        #发送后增加已发送的次数
        count = len(phone.split(','))
        total_used_count += count
        single_times += 1
        print(type(total_used_count),total_used_count)
        # setattr(sms_cfg_obj, total_used_count, total_used_count)
        sms_cfg_obj.total_used_count = total_used_count
        setattr(sms_cfg_obj, sms_type, single_times)
        sms_cfg_obj.save()
        #记录发送的短信到数据库
        dic = {'sms_type': sms_type,
               'send_msg': msg, 
               'send_phones': phone,
               'send_status': '1'}
        from myapps.tora_monitor import models as mmodels
        mmodels.SmsRecordData.objects.create(**dic)
        
    else:
        logger.error("已超过当天可发送的短信总数：%d 条" % total_count)