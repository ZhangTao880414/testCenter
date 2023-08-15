#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   res_pool_manager.py
@Time    :   2021/04/01 14:39:32
@Author  :   wei.zhang 
@Version :   2.0
@Desc    :   None
'''

# here put the import lib
import pandas as pd
import numpy as np
import json
import datetime as dt
import logging
#import mysql_tools_class as myc
import common_tools as ct
import no_pass_ssh as nssh
import os
from myapps.toraapp import models as tmodels
from django.forms.models import model_to_dict
from django.conf import settings
from django.core.mail import send_mail
from threading import Thread
from django.db import connection, transaction
import tora_django_common as tdc


#ndates = dt.datetime.now().strftime("%Y-%m-%d")
#ntimes = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#logger = logging.getLogger()
logger = logging.getLogger('django')

class res_pool_manager:

    def __init__(self, task_id):
        self.oper = 'auto_tora'
        self.task_id = task_id
        # db_info = []
        # self.mysql_obj = myc.mysql_tools(db_info)


    #更新sys_user,vpn_user,net_access字段，根据字段apply_id更新更新
    def auto_assign_success(self,res_msg):
        #成功更新语句
        update_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # update_res_success = "UPDATE tora_oper_data.resource_apply_info \
        #                 SET req_status = '1', res_msg = '%s', operator = '%s',update_time = '%s' \
        #                 WHERE apply_id = '%s'" % (res_msg,self.oper,update_time,apply_id)
        
        # res = self.mysql_obj.execute_sql_noclose(update_res_success)
        task_obj = tmodels.TaskFlow.objects.get(id=self.task_id)
        task_obj.task_status = '1'
        res = task_obj.save()
        print("auto_assign_success_res:", res)
        #更新表ops_oper_log
        if res == None:
            return 1
        else:
            return 0

    #更新失败状态
    def auto_assign_failed(self,res_msg):
        #更新resource_apply字段
        update_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # update_res_failed = "UPDATE tora_oper_data.resource_apply_info \
        #                 SET req_status = '9', res_msg = '%s', operator = '%s',update_time = '%s' \
        #                 WHERE apply_id = '%s'" % (res_msg,self.oper,update_time,apply_id)
        
        # res = self.mysql_obj.execute_sql_noclose(update_res_failed)
        task_obj = tmodels.TaskFlow.objects.get(id=self.task_id)
        task_obj.task_status = '9'
        if task_obj.comment != None:
            task_obj.comment += res_msg
        task_obj.comment = res_msg  
        res = task_obj.save()
        #更新表ops_oper_log
        print("auto_assign_failed_res:", res)
        if res == None:
            return 1
        else:
            return 0


    #更新表share_servers_info字段assigned_count,参数1为加1，-1为减一个
    def update_assigned_count(self,inner_ip,customer_id,i):
        #先查询之前的数量
        ShareServer_obj = tmodels.ShareServerInfo.objects.filter(machine__inner_ip=inner_ip).first()
        # b=tmodels.ShareServerInfo.objects.filter(machine__inner_ip='192.168.80.119').first()
        # b=tmodels.ShareServerInfo.objects.filter(machine__inner_ip='192.168.80.9').first()
        #print(ShareServer_obj)
        if ShareServer_obj == None:
            logger.error("服务器inner_ip %s没有在资源池" % (inner_ip))
            return 0
        else:
            #pre_data = ShareServer_obj.assigned_count
            cust_obj = tmodels.ToraCustomer.objects.filter(pk=customer_id).first()
            if i==1:
                ShareServer_obj.assigned_cust.add(cust_obj)
            else:
                ShareServer_obj.assigned_cust.remove(cust_obj)
            ShareServer_obj.assigned_count += i
            res = ShareServer_obj.save()
            if res == None:
                return 1
            else:
                return 0

    #分配系统用户
    def assign_sys_user(self,customer_id,inner_ip):
        #唯一性校验
        # unique_query_sql = "SELECT sys_user_name \a
        #                 FROM tora_oper_data.server_users_info \
        #                 WHERE inner_ip = '%s' and nsight_user = '%s' and cur_status = '1'" % (inner_ip,nsight_user)
        # unique_user = self.mysql_obj.get_db_df(unique_query_sql)
        unique_user = tmodels.SystemUserInfo.objects.filter(inner_ip=inner_ip,customer_id=customer_id)
        #user = tmodels.SystemUserInfo.objects.filter(inner_ip='192.168.10.1',customer_id='2')
        print("unique_user:", len(unique_user))
        if len(unique_user) > 0:
            #print(unique_user[0])
            err_msg = 'inner_ip: %s,customer_id %s，已分配过用户' % (inner_ip,customer_id)
            logger.error(err_msg)
            #更新申请表状态失败
            res = self.auto_assign_failed(err_msg)
            return 0
        else:
            logger.info("sys_user唯一性校验通过")

        #空余用户
        # query_sys_user = "SELECT sys_user_name, sys_user_passwd \
        #                 FROM tora_oper_data.server_users_info \
        #                 WHERE inner_ip = '%s' and cur_status = '0'" % (inner_ip)
        # avalibe_user = self.mysql_obj.get_db_df(query_sys_user)
        # #最好后续再做个按结尾数字排序
        # # print(avalibe_user)
        # # print(avalibe_user.iloc[0]['sys_user_name'])
        # # avalibe_user.sort_values(by="sys_user_name",axis=0,ascending=True,inplace=True)
        # # print(avalibe_user)
        avalible_user = tmodels.SystemUserInfo.objects.filter(inner_ip=inner_ip, cur_status='0').order_by('id')
        #avalibe_user = tmodels.SystemUserInfo.objects.filter(inner_ip='192.168.80.9',cur_status='0').order_by('id')
        print("len(avalible_user):", len(avalible_user))
        if (len(avalible_user)==0):
            msg = "服务器%s 没有系统用户可分配给申请ID:%s!" % (inner_ip, self.task_id)
            logger.error(msg)
            #更新申请记录为失败状态
            res = self.auto_assign_failed(msg)
            return 0
        else:
            # sys_user_name = avalibe_user.iloc[0]['sys_user_name']
            # sys_user_passwd = avalibe_user.iloc[0]['sys_user_passwd']
            # update_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # #update resource_apply_info and server_users_info
            # update_resource_apply = "UPDATE tora_oper_data.resource_apply_info \
            #             SET sys_user_name = '%s', sys_user_passwd = '%s',operator = '%s',update_time = '%s' \
            #             WHERE apply_id = '%s' " % (sys_user_name,sys_user_passwd,self.oper,update_time,apply_id)
            # res1 = self.mysql_obj.execute_sql_noclose(update_resource_apply)
            # #置状态为1，更新nsight_user
            # update_server_users = "UPDATE tora_oper_data.server_users_info \
            #             SET cur_status = '1', nsight_user = '%s', operator = '%s',update_time = '%s'\
            #             WHERE sys_user_name = '%s' and inner_ip = '%s'" % (nsight_user,self.oper,update_time,sys_user_name,inner_ip)
            # res2 = self.mysql_obj.execute_sql_noclose(update_server_users)
            # #更新表share_servers_info字段assigned_count

            res_update = self.update_assigned_count(inner_ip,customer_id,1)
            # if res_update:
            #     logger.info("ok,更新assigned_count成功！")
            # else:
            #     logger.error("error,更新assigned_count失败！")
            # res = res1 and res2
            avalible_user[0].customer_id = customer_id
            avalible_user[0].cur_status = '1'
            res = avalible_user[0].save()

            choice_outer_ip = tmodels.ShelfMachine.objects.get(inner_ip=inner_ip).outer_ip
            choice_os = tmodels.ShelfMachine.objects.get(inner_ip=inner_ip).os
            task_obj = tmodels.TaskFlow.objects.get(id=self.task_id)
            task_obj.inner_ip = inner_ip
            task_obj.outer_ip = choice_outer_ip
            task_obj.os = choice_os
            task_obj.sys_user_name = avalible_user[0].sys_user_name
            task_obj.sys_user_passwd =  avalible_user[0].sys_user_passwd
            task_obj.save()

            if res == None:
                logger.info("用户分配保存成功")
                return 1
            else:
                logger.info("用户分配保存失败")
                return 0



    # #分配vpn
    # def process_vpn_user(self,task_data):
    #     #唯一性校验
    #     unique_vpn_qsql = "SELECT vpn_user_name \
    #                     FROM tora_oper_data.vpn_users_info \
    #                     WHERE engine_room = '%s' and nsight_user = '%s' and cur_status = '1'" % (engine_room,nsight_user)
    #     unique_user = self.mysql_obj.get_db_df(unique_vpn_qsql)
    #     if len(unique_user) > 0:
    #         err_msg = 'engine_room: %s,nsight_user %s，已分配过vpn用户:%s' % (engine_room,nsight_user,unique_user.iloc[0]['vpn_user_name'])
    #         logger.error(err_msg)
    #         #更新申请表状态失败
    #         res = self.auto_assign_failed(apply_id,err_msg)
    #         return 0
    #     else:
    #         logger.info("vpn_user唯一性校验通过")
    #     #空余用户
    #     query_vpn_user = "SELECT vpn_address,vpn_user_name, vpn_user_passwd \
    #                     FROM tora_oper_data.vpn_users_info \
    #                     WHERE engine_room = '%s' and cur_status = '0'" % (engine_room)
    #     avalibe_user = self.mysql_obj.get_db_df(query_vpn_user)
    #     print("vpn_user:",avalibe_user)
    #     if (len(avalibe_user)==0):
    #         msg = "机房[%s]没有vpn账号可分配给申请ID:%s!" % (engine_room,apply_id)
    #         logger.error(msg)
    #         #更新申请记录为失败状态
    #         res = self.auto_assign_failed(apply_id,msg)
    #         return res
    #     else:
    #         vpn_address = avalibe_user.iloc[0]['vpn_address']
    #         vpn_user_name = avalibe_user.iloc[0]['vpn_user_name']
    #         vpn_user_passwd = avalibe_user.iloc[0]['vpn_user_passwd']
    #         update_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #         #update resource_apply_info and vpn_users_info
    #         update_resource_apply = "UPDATE tora_oper_data.resource_apply_info \
    #                     SET vpn_address = '%s', vpn_user_name = '%s', vpn_user_passwd = '%s',operator = '%s',update_time = '%s' \
    #                     WHERE apply_id = '%s' " % (vpn_address,vpn_user_name,vpn_user_passwd,self.oper,update_time,apply_id)
    #         res1 = self.mysql_obj.execute_sql_noclose(update_resource_apply)
    #         #置状态为1，更新nsight_user
    #         update_vpn_users = "UPDATE tora_oper_data.vpn_users_info \
    #                     SET cur_status = '1', nsight_user = '%s', operator = '%s',update_time = '%s' \
    #                     WHERE vpn_user_name = '%s' and engine_room = '%s'" % (nsight_user,self.oper,update_time,vpn_user_name,engine_room)
    #         res2 = self.mysql_obj.execute_sql_noclose(update_vpn_users)
    #         res = res1 and res2
    #         return res

    #处理网络申请,分配或者回收
    def process_access_apply(self):
        try:
            #根据apply_id去查询状态是0状态，0,待设置;1,已设置;9,处理失败''
            #logger.info("access_action为0，不需要申请网络")
            # query_access_record = "SELECT id,apply_id,inner_ip,access_action,customer_ip,customer_ports,cur_status \
            #                 FROM tora_oper_data.access_apply_info \
            #                 WHERE apply_id = '%s' and cur_status = '0' " % (apply_id)
            # accsess_records = self.mysql_obj.get_db_df(query_access_record)

            access_querySet = tmodels.AccessApplyInfo.objects.filter(task_id=self.task_id, cur_status='0')
            
            if (len(access_querySet)==0):
                msg = "资源申请ID：%s 没有待处理的网络申请!" % str(self.task_id)
                logger.info(msg)
                return 1
            else:
                acc_error = []
                #for index, row in accsess_records.iterrows(): 
                for access_obj in access_querySet:
                    row = model_to_dict(access_obj)
                    id = row['id']
                    #apply_id = row['apply_id']
                    inner_ip = row['inner_ip']
                    share_server = tmodels.ShareServerInfo.objects.filter(machine__inner_ip=inner_ip)
                    if len(share_server) == 0:
                        logger.error("服务器%s不在资源池里，不能自动设置网络访问" % inner_ip)
                        return 0
                    outer_ip = row['outer_ip']
                    access_action  = row['access_action']
                    customer_ip = row['customer_ip']
                    customer_ports = row['customer_ports']
                    #cur_status = row['cur_status']
                    #设置防火墙
                    res_set = self.set_iptables(inner_ip,access_action,customer_ip,customer_ports)
                    if res_set:
                        #置状态为1已设置
                        new_status = '1'
                        msg = "id[%s],access_action[%s],iptables设置成功！" % (id,access_action)
                        logger.info(msg)
                    else:
                        #置状态为9已回收
                        new_status = '9'
                        acc_error.append(str(id))
                        msg = "id[%s],access_action[%s],iptables设置失败！" % (id,access_action)
                        logger.error(msg)
                    # update_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # update_access_status_sql = "UPDATE tora_oper_data.access_apply_info \
                    #                             SET cur_status = '%s',operator = '%s',update_time = '%s',res_msg = '%s' \
                    #                             WHERE id = '%s' " % (new_status,self.oper,update_time,msg,id)
                    # update_res = self.mysql_obj.execute_sql_noclose(update_access_status_sql) 
                    access_obj.cur_status = new_status
                    update_res = access_obj.save()
                    logger.info("update_access_status执行结果:")
                    logger.info(update_res)
                print("acc_error:",acc_error)
                if len(acc_error) != 0:
                    err_msg = "网络申请id[%s]处理失败!" % (';'.join(acc_error))
                    logger.error(err_msg)
                    #更新申请记录为失败状态
                    res = self.auto_assign_failed(err_msg)
                    return 0
                else:
                    return 1
        except Exception as e:
            err_msg = '网络申请处理异常'
            logger.error('网络申请处理异常', exc_info=True)
            res = self.auto_assign_failed(err_msg)
            #res = 0
            print(str(e))
            return 0
        finally:
            logger.info("no close")
            #mysql_obj.ms_close()
        

    #设置防火墙，默认处理外网授权direction = '0'
    def set_iptables(self,inner_ip,access_action,customer_ip,customer_ports,direction = '0'):
        #解析是否正确,多个端口以|隔开；连续端口可采用格式，例：9980~9990;例如10.188.172.13:3333~3340|3345|5566
        #access_action1,新增;2，移除
        print("access_action:",access_action)
        if access_action == '1':
            action_para = '-I'
        elif access_action == '2':
            action_para = '-D'
        else:
            print("accee_action值不正确！")
            return -1
        ports = str(customer_ports).split('|')
        ports_list = {"series":[],"multi":[]}
        for item in ports:
            if '~' in str(item):
                ports_list["series"].append(item.strip())
            else:
                ports_list["multi"].append(item.strip())
        print(ports_list)
        exe_shell_list = []
        if len(ports_list["multi"]) != 0 :
            exe_ports = ','.join(ports_list["multi"])
            #exe_shell_list.append("iptables %s OUTPUT -d %s -p tcp -m state --state NEW -m tcp --dport %s -j ACCEPT" % (action_para,customer_ip,exe_ports))
            exe_shell_list.append("iptables %s OUTPUT -d %s -p tcp -m state --state NEW -m multiport --dport %s -j ACCEPT" % (action_para,customer_ip,exe_ports))
        if len(ports_list["series"]) != 0 :
            for item in ports_list["series"]:
                exe_ports = item.replace("~",":")
                exe_shell_list.append("iptables %s OUTPUT -d %s -p tcp -m state --state NEW -m multiport --dport %s -j ACCEPT" % (action_para,customer_ip,exe_ports))
        print(exe_shell_list)
        res = []
        nssh_obj = nssh.Rsa_Key_SSH(inner_ip,'22','root','/home/trade/.ssh/id_rsa')
        for exe_shell in exe_shell_list:
            print("exe_shell:",exe_shell)
            exe_res = nssh_obj.exec(exe_shell)
            print("exe_res:",exe_res)
            if exe_res == ['']:
                res.append(1)
                print("执行成功")
            else:
                res.append(0)
                print("执行失败")
        save_res = nssh_obj.exec('service iptables save')
        print(save_res)
        res_flag = (sum(res) == len(res))
        return res_flag


    #更新日志表
    def update_log(self,log_info):
        #log_info = ['sys_user','add','add user2','nsight_user1','commemnt','zw']
        # insert_log = "INSERT INTO tora_oper_data.ops_oper_log(action,action_type, \
        #     action_detail,nsight_user,comment,operator) \
        #    VALUES ('%s','%s', '%s', '%s','%s','%s')" % \
        #    ('sys_user','add','add user2','nsight_user1','commemnt','zw')
        insert_log = "INSERT INTO tora_oper_data.ops_oper_log(function,action_type, \
            action_detail,opt_object,comment,operator) \
        VALUES ('%s','%s', '%s', '%s','%s','%s')" % \
        (log_info[0],log_info[1],log_info[2],log_info[3],log_info[4],log_info[5])
        msg = '#'.join(log_info)
        logger.info(msg)

        res = self.mysql_obj.execute_sql_noclose(insert_log)
        return res

    #回收资源,
    #def release_resource(self,apply_id,customer_id,engine_room,inner_ip):
    def release_resource(self):
        update_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #清理服务器/home/user目录，将user删除重建,暂时手工处理
        task_obj = tmodels.TaskFlow.objects.get(id=self.task_id)
        msg = "task_id: %s 客户：%s, inner_ip: %s,需要回收资源！" % (self.task_id, task_obj.custgroup_name, task_obj.inner_ip)
        ct.send_sms_control('NoLimit',msg,'13681919346')
        #更新vpn表nsight_user字段置空，修改状态为2待回收
        # update_vpn_users = "UPDATE tora_oper_data.vpn_users_info \
        #             SET cur_status = '2', nsight_user = '', operator = '%s',update_time = '%s' \
        #             WHERE engine_room = '%s' and nsight_user = '%s'" % (self.oper,update_time,engine_room,nsight_user)
        # res_vpn = self.mysql_obj.execute_sql_noclose(update_vpn_users)
        
        vpn_name_list = task_obj.vpn_user_name.split(';')
        vpn_phone_list = task_obj.vpn_phone.split(';')
        vpn_df = pd.DataFrame({'vpn_name': vpn_name_list, 'vpn_phone': vpn_phone_list})
        for row in vpn_df.itertuples():
            vpn_obj = tmodels.VpnUserInfo.objects.filter(engine_room=task_obj.engine_room, vpn_user_name=getattr(row, 'vpn_name')).first()
            if vpn_obj:
                res_vpn = tdc.release_vpnuser_resource(task_obj.engine_room, task_obj.custgroup_name, getattr(row, 'vpn_name'), getattr(row, 'vpn_phone'), task_obj.inner_ip)
            else:
                logger.error("机房：%s, 没用该vpn：%s 记录!" % (task_obj.engine_room, getattr(row, 'vpn_name')))
                res_vpn = 0
            if res_vpn:
                logger.info("更新vpn_users_info成功")
            else:
                msg = "释放vpn用户表失败！机房：%s, vpn：%s, inner_ip: %s" % (task_obj.engine_room, getattr(row, 'vpn_name'), task_obj.inner_ip)
                logger.error(msg)
        #将系统用户表nsight_user字段置空，修改状态为2待回收
        # update_server_users = "UPDATE tora_oper_data.server_users_info \
        #             SET cur_status = '2', nsight_user = '', operator = '%s',update_time = '%s'\
        #             WHERE inner_ip = '%s' and nsight_user = '%s'" % (self.oper,update_time,inner_ip,nsight_user)
        # res_sys = self.mysql_obj.execute_sql_noclose(update_server_users)
        sys_user_obj = tmodels.SystemUserInfo.objects.filter(inner_ip=task_obj.inner_ip, sys_user_name=task_obj.sys_user_name).first()
        if sys_user_obj:
            sys_user_obj.cur_status = '2'
            sys_user_obj.save()
            res_sys = 1
        else:
            res_sys = 0

        if res_sys:
            #将assigned_count数量减一
            res_update = self.update_assigned_count(task_obj.inner_ip,task_obj.customer_id,-1)
        else:
            msg = "更新server_users_info表失败！ 系统用户 '%s', inner_ip = '%s'" % (task_obj.sys_user_name, task_obj.inner_ip)
            logger.error(msg)
            res_update = 0
        return res_update


    def auto_add_access_apply(self):
        task_obj = tmodels.TaskFlow.objects.get(id=self.task_id)
        #插入网络申请表
        if task_obj.access_action != '0' and task_obj.access_address != None:
            #默认OA行为字段设置为0放行，方向为0外网授权,。
            behaviour = '0'
            direction = '0'
            #解析access_address
            access_list = task_obj.access_address.split(';')
            try:
                for access_item in access_list:
                    tem_list = access_item.split(':')
                    customer_ip = tem_list[0]
                    customer_ports = tem_list[1]

                    tmodels.AccessApplyInfo.objects.create(task=task_obj,
                                                        customer=task_obj.customer,
                                                        inner_ip=task_obj.inner_ip,
                                                        outer_ip=task_obj.outer_ip,
                                                        customer_ip=customer_ip,
                                                        customer_ports=customer_ports,
                                                        cur_status='0',
                                                        operator=task_obj.operator)
                return 1
            except Exception:
                return 0
            return res
        else:
            logger.info("access_action为0，access_address为None,不需要申请网络")
            return 1

    @ct.async_run
    def process_resource_apply(self):
        #查询req_status状态为0的记录,0,待处理;1,已完成;4,已拒绝;9,失败'

        # apply_obj = tmodels.TaskFlow.objects.filter(task_status='0')
        # if len(apply_obj) != 0:
        #     for obj in apply_obj:
                # id = obj.__getattribute__('id')
                # inner_ip = obj.__getattribute__('inner_ip')
                # customer = obj.__getattribute__('customer')
                # task_type = obj.__getattribute__('task_type')
                # print(id,inner_ip,customer)
        obj = tmodels.TaskFlow.objects.get(id=self.task_id)
        task_data = model_to_dict(obj)
        print("task_data:", task_data)
        if task_data['task_status'] == '0':
            #6共享资源申请
            if task_data['task_type'] == '6':
                print("自动处理task_id %s" % task_data['id'])
                if task_data['inner_ip'] != None:
                    #分配系统用户
                    rep_sys = self.assign_sys_user(str(task_data['customer']), task_data['inner_ip'])

                elif task_data['os'] in ['redhat','centos','ubuntu'] and task_data['os_version'] != None:
                    choice_inner_ip = tdc.choice_share_server(task_data['engine_room'],task_data['os'],task_data['os_version'],task_data['node_no'])
                    choice_outer_ip = tmodels.ShelfMachine.objects.get(inner_ip=choice_inner_ip).outer_ip
                    rep_sys = self.assign_sys_user(task_data['id'], str(task_data['customer']), choice_inner_ip)
                else:
                    rep_sys = 0
                    error_msg = "os,os_version为空，无法给task_id: %s,自动分配资源！" % task_data['id']
                    logger.error(error_msg)
                    self.auto_assign_failed(task_data['id'], error_msg)

                #增加网络访问记录
                print("task_data['access_action']:", task_data['access_action'], task_data['outer_ip'])
                #if task_data['outer_ip'] != None and task_data['access_action'] != '0' :
                if task_data['access_action'] != '0' :
                    add_access = self.auto_add_access_apply()
                    #自动设置网络访问
                    if add_access:
                        rep_acc = self.process_access_apply()
                    else:
                        rep_acc = 0
                elif task_data['access_action'] == '0':
                    rep_acc = 1
                    logger.error("任务%s没有outer_ip或者没有网络访问需求，不需要自动网络处理" % str(task_data['id']))

                # else:
                #     rep_acc = 0
                #     logger.error("任务%s没有outer_ip，无法自动网络处理" % str(task_data['id']))


                total_res = rep_sys and rep_acc

            #只处理外网授权网络申请,资源池的机器才可以自动处理
            elif task_data['task_type'] == '8':
                #增加网络访问记录
                if task_data['access_action'] != '0' :
                    add_access = self.auto_add_access_apply()
                    #自动设置网络访问
                    if add_access:
                        total_res = self.process_access_apply()
                    else:
                        total_res = 0
                elif task_data['access_action'] == '0':
                    total_res = 1
                    logger.error("任务%s没有outer_ip或者没有网络访问需求，不需要自动网络处理" % str(task_data['id']))

                else:
                    total_res = 0
                    logger.error("任务%s没有outer_ip，无法自动网络处理" % str(task_data['id']))
            #客户申请回收资源
            elif task_data['task_type'] == '7':
                total_res = self.release_resource()
            #操作员强制回收资源
            elif task_data['task_type'] == '9':
                total_res = self.release_resource()
            #其他
            else:
                logger.info("task_id: %s 其他状态不做自动处理" % task_data['id'])
                total_res = 0
            
            if total_res == 1:
                res_msg = '申请记录：%s处理成功' % task_data['id']
                logger.info(res_msg)
                update_res = self.auto_assign_success(res_msg)

            else:
                # #处理失败，不需要更新req_status状态，失败的地方会处理
                # err_msg = '申请记录：%s处理失败' % apply_id
                # logger.info(err_msg)
                # #更新失败状态为9，不更新res_msg
                # update_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # update_res_failed = "UPDATE tora_oper_data.resource_apply_info \
                #                 SET req_status = '9', operator = '%s',update_time = '%s' \
                #                 WHERE apply_id = '%s'" % (self.oper,update_time,apply_id)                    
                # res_fail = self.mysql_obj.execute_sql_noclose(update_res_failed)
                pass
        else:
            logger.info("task_status非0，不自动处理")
            total_res = 0

        #self.mysql_obj.ms_close()
        #print("total_res:",total_res)
        return total_res


def main():
    try:
        yaml_path = './config/ops_manager_logger.yaml'
        ct.setup_logging(yaml_path)

        info = ct.get_server_config('./config/mysql_config_ns.txt')
        # mysql_db_ip = info[0][0]
        # mysql_user = info[0][1]
        # mysql_passwd = info[0][2]
        # mysql_dbname = info[0][3]
        # mysql_port = int(info[0][4])
        mysqldb_info = [info[0][0],info[0][1],info[0][2],info[0][3],int(info[0][4])]
        res_manager = res_pool_manager(mysqldb_info)
        pro_res = res_manager.process_resource_apply()
        print(pro_res)
        if pro_res == 1:
            print("处理成功")
        else:
            print("处理失败") 
    except Exception:
        logger.error('Faild to run res_pool_manager!', exc_info=True)
        return 0
        #ct.send_sms_control('13681919346',"nsight申请处理异常！")
    finally:
        for handler in logger.handlers:
            logger.removeHandler(handler)


if __name__ == "__main__":
    main()
