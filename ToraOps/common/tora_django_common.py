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

#根据节点的ID查询对应行情信息
def get_nodeConfig(node):
    
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
                nodeobj = tmodels.NodeInfo.objects.get(pk=node)
                #获取行情名字为主键
                #mq1 = nodeobj.mq.all()[0]
                #mq_name = mq1.mq_name
                #mq_name = nodeobj.mq.mq_group_name
                mq_obj = tmodels.ToraMq.objects.filter(mq_group=nodeobj.mq, business=item_busi, mq_type=item_mq, tele_pattern=item_tele).first()
                for item_value in ['ip_addr','port', 'md_rec_addr', 'source_ip']:
                    if mq_obj:
                        print(nodeobj.mq, item_busi, item_mq,item_tele)
                        nodeConfig[item_busi]['mq'][item_mq][item_tele][item_value] = mq_obj.__getattribute__(item_value)
                    else:
                        nodeConfig[item_busi]['mq'][item_mq][item_tele][item_value] = ''

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
    print("cust_obj:", cust_obj)
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
    print("is_created:", is_created)
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
    for item_bussi in ['hxzq','sp','rzrq']:
        #是否有交易环境
        if nodeConfig[item_bussi]['trade']['tradeserver1']['ip_addr'] != '':
            #先写md_L2
            if nodeConfig[item_bussi]['mq']['md_L2']['udp']['ip_addr'] != '':
                content_hxzq_md_L2_udp = """【{3}】
                    沪&深L2 组播地址：udp://{0}:{1}
                    (使用{2}地址段（具体以邮件为准）收取、SourceIP：NULL)
                    #RegisterMulticast("udp://{0}:{1}","{2}",NULL)
                    """.format(nodeConfig[item_bussi]['mq']['md_L2']['udp']['ip_addr'], nodeConfig[item_bussi]['mq']['md_L2']['udp']['port'],
                                nodeConfig[item_bussi]['mq']['md_L2']['udp']['md_rec_addr'],business[item_bussi])
            else:
                content_hxzq_md_L2_udp = """【{0}】
                    """.format(business[item_bussi])
            content += content_hxzq_md_L2_udp
            #剩余其他行情信息和交易信息
            content_hxzq_second = ''
            if node_no == '4' and item_bussi == 'hxzq':
                content_hxzq_second = """
                    L1沪&深行情(MD)交易(TD) FENS的双路地址: tcp://{0}:{1},tcp://{2}:{3}
                    #注册单个fens地址，如：RegisterNameServer("tcp://{0}:{1}")
                    #注册多个fens地址用逗号连接，如：RegisterNameServer("tcp://{0}:{1},tcp://{2}:{3}")（推荐方式）       
                    """.format(nodeConfig[item_bussi]['trade']['fens1']['ip_addr'],nodeConfig[item_bussi]['trade']['fens1']['port'],
                                    nodeConfig[item_bussi]['trade']['fens2']['ip_addr'],nodeConfig[item_bussi]['trade']['fens2']['port'])
                # else:
                #     content_hxzq_second = """
                #         交易前置(TD)：tcp://{0}:{1}
                #         """.format(nodeConfig[item_bussi]['trade']['trade_front1']['ip_addr'],nodeConfig[item_bussi]['trade']['trade_front1']['port'])
            #非宛平hxzq节点
            else:
                if nodeConfig[item_bussi]['mq']['sse_md_L2']['udp']['ip_addr'] != '':
                    content_hxzq_sse_md_L2 = """
                        沪L2组播行情: udp://{0}:{1}
                        (使用{2}地址段收取、SourceIP：NULL)
                        """.format(nodeConfig[item_bussi]['mq']['sse_md_L2']['udp']['ip_addr'],nodeConfig[item_bussi]['mq']['sse_md_L2']['udp']['port'],
                                    nodeConfig[item_bussi]['mq']['sse_md_L2']['udp']['md_rec_addr'])
                    content_hxzq_second += content_hxzq_sse_md_L2

                if nodeConfig[item_bussi]['mq']['szse_md_L2B']['udp']['ip_addr'] != '':
                    content_hxzq_szse_md_L2B = """
                        深L2 FPGA组播行情：udp://{0}:{1}
                        (使用{2}地址段收取、SourceIP：NULL)
                        """.format(nodeConfig[item_bussi]['mq']['szse_md_L2B']['udp']['ip_addr'],nodeConfig[item_bussi]['mq']['szse_md_L2B']['udp']['port'],
                                    nodeConfig[item_bussi]['mq']['szse_md_L2B']['udp']['md_rec_addr'])
                    content_hxzq_second += content_hxzq_szse_md_L2B

                if nodeConfig[item_bussi]['mq']['szse_md_L2A']['udp']['ip_addr'] != '':
                    content_hxzq_szse_md_L2A = """
                        深L2 软解组播行情：udp://{0}:{1}
                        (使用{2}地址段收取、SourceIP：NULL)
                        """.format(nodeConfig[item_bussi]['mq']['szse_md_L2A']['udp']['ip_addr'],nodeConfig[item_bussi]['mq']['szse_md_L2A']['udp']['port'],
                                    nodeConfig[item_bussi]['mq']['szse_md_L2A']['udp']['md_rec_addr'])
                    content_hxzq_second += content_hxzq_szse_md_L2A

                if nodeConfig[item_bussi]['mq']['md_L2']['tcp']['ip_addr'] != '':
                    content_hxzq_md_L2_tcp = """
                        沪&深L2 TCP行情：tcp://{0}:{1}
                        """.format(nodeConfig[item_bussi]['mq']['md_L2']['tcp']['ip_addr'],nodeConfig[item_bussi]['mq']['md_L2']['tcp']['port'])
                    content_hxzq_second += content_hxzq_md_L2_tcp

                if nodeConfig[item_bussi]['mq']['md_L1']['udp']['ip_addr'] != '':
                    content_hxzq_md_L1_udp = """
                        沪&深L1组播行情：udp://{0}:{1}
                        (使用{2}地址段收取、SourceIP：NULL)
                        """.format(nodeConfig[item_bussi]['mq']['md_L1']['udp']['ip_addr'],nodeConfig[item_bussi]['mq']['md_L1']['udp']['port'],
                                    nodeConfig[item_bussi]['mq']['md_L1']['udp']['md_rec_addr'])
                    content_hxzq_second += content_hxzq_md_L1_udp

                if nodeConfig[item_bussi]['mq']['md_L1']['tcp']['ip_addr'] != '':
                    
                    port_list = (nodeConfig[item_bussi]['mq']['md_L1']['tcp']['port']).split('|')
                    if len(port_list) == 2:
                        content_hxzq_md_L1_tcp = """
                            沪&深L1 TCP行情：tcp://{0}:{1}
                            (沪深行情合并推送到单一前置，两个端口为互备端口，当一个故障时会自动切换到另一个推送行情，建议同时注册)
                            """.format(nodeConfig[item_bussi]['mq']['md_L1']['tcp']['ip_addr'],nodeConfig[item_bussi]['mq']['md_L1']['tcp']['port'])
                    else:
                        content_hxzq_md_L1_tcp = """
                        沪&深L1 TCP行情：tcp://{0}:{1}
                        """.format(nodeConfig[item_bussi]['mq']['md_L1']['tcp']['ip_addr'],nodeConfig[item_bussi]['mq']['md_L1']['tcp']['port'])
                    content_hxzq_second += content_hxzq_md_L1_tcp

                if item_bussi == 'hxzq':
                    content_hxzq_trade = """
                        交易核心(TD)：tcp://{0}:{1}
                        """.format(nodeConfig[item_bussi]['trade']['tradeserver1']['ip_addr'],nodeConfig[item_bussi]['trade']['tradeserver1']['port'])
                    content_hxzq_second += content_hxzq_trade
                else:
                    content_hxzq_trade = """交易前置(TD)：tcp://{0}:{1}
                        """.format(nodeConfig[item_bussi]['trade']['trade_front1']['ip_addr'],nodeConfig[item_bussi]['trade']['trade_front1']['port'])
                    content_hxzq_second += content_hxzq_trade
            
            content += content_hxzq_second

    if nodeConfig['qh']['mq']['qh_L1']['tcp']['ip_addr'] != '':
        context_qh = """
            【期货】
            期货L1行情(MD): tcp://{0}:{1}  
            """.format(nodeConfig['qh']['mq']['qh_L1']['tcp']['ip_addr'],nodeConfig['qh']['mq']['qh_L1']['tcp']['port'])
        content += context_qh
    
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


#取所有的choices配置
def get_choices():
    config_path = os.path.join(settings.BASE_DIR, "config")
    choices_file = os.path.join(config_path,'form_choices.json')
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


def get_cust_phone(hostip):
    #hostip = '192.168.10.214'
    try:
        machine_obj = tmodels.ShelfMachine.objects.get(inner_ip=hostip)
        machine_owner = machine_obj.owner
        cust_obj = tmodels.ToraCustomer.objects.get(id=machine_owner.id)
        cust_phone = cust_obj.phone
    except Exception as e:
        msg = "服务器%s, 取客户手机号码出现异常!" % hostip
        logger.error(msg)
        cust_phone = None
    return cust_phone


def get_opm_phone(custgroup_name='全创运维组'):

    try:
        opm_obj = tmodels.ToraCustomer.objects.get(custgroup_name=custgroup_name)
        opm_phone = opm_obj.phone
    except Exception as e:
        msg = "取运维组手机号码出现异常!" 
        logger.error(msg)
        opm_phone = None
    return opm_phone


#导入独用的客户服务器信息
@ct.async_run
def import_cust_machine():
    pddata = pd.read_csv('./config/cust_machine_0810.csv', encoding='gbk', keep_default_na=False)
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
        cabinet = getattr(row, 'cabinet')
        unit = getattr(row, 'unit')
        model = getattr(row, 'model')
        serial_number = getattr(row, 'serial_number')
        IT_checked_number = getattr(row, 'IT_checked_number')
        configuration = getattr(row, 'configuration')
        node_name = getattr(row, 'node_name')
        use_status = getattr(row, 'use_status')
        opertaion_system = getattr(row, 'opertaion_system')
        inner_ip = getattr(row, 'inner_ip')
        outer_ip = getattr(row, 'outer_ip')
        high_trade_ip = getattr(row, 'high_trade_ip')
        high_mqA_ip = getattr(row, 'high_mqA_ip')
        high_mqB_ip = getattr(row, 'high_mqB_ip')
        ipmi_ip = getattr(row, 'ipmi_ip')
        note = getattr(row, 'note')
        disk_serial = getattr(row, 'disk_serial_number')
        custgroup_name = getattr(row, 'custgroup_name')
        shelf_time = getattr(row, 'shelf_time')
        buyer = getattr(row, 'buyer')
        comment = getattr(row, 'comment')



        if assert_type_str == '虚拟机':
            assert_type = '2'
        elif assert_type_str == '交换机':
            assert_type = '4'
        else:
            assert_type = '1'

        #print("test:::",model, model=='')
        if model:
            band_models = model.split()
            server_brand = band_models[0]
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
            nodeobj = tmodels.NodeInfo.objects.get_or_create(
                                node_no='00',
                                defaults={'engine_room': engine_room,
                                'node_name': engine_room + '_空节点'})
        if shelf_time == '老' or shelf_time == '':
            shelf_date = '2010-01-01'
        else:
            #shelf_date = time.mktime(time.strptime(shelf_time, "%Y年%M月%d日"))
            date_str = shelf_time.replace('年','-').replace('月','-').replace('日','')
            date_list = date_str.split('-')
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
        cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
        if buyer == '客户自购':
            cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
            owner_obj = cust_obj
        elif buyer == '华鑫采购':
            hxzq_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='华鑫证券').first()
            owner_obj = hxzq_obj
        else:
            qckj_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='全创科技').first()
            owner_obj = qckj_obj
        purpose = '1'
 
        cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
        owner_obj = cust_obj
        machine_obj, is_created = tmodels.ShelfMachine.objects.get_or_create(
                        engine_room=engine_room,
                        inner_ip=inner_ip,
                        serial_number=serial_number,
                        defaults={'engine_room': engine_room,
                                'assert_number': assert_number,
                                'assert_type': assert_type,
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
        cust_set =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name)
        machine_obj.customer.set(cust_set)
        