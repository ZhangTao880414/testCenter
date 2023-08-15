#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   vpn_data_syn.py
@Time    :   2021/06/24 14:35:45
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   同步vpn服务器的账号和资源列表到django的数据后台
'''

# here put the import lib
# import os
# import sys
# import django
# BASE_DIR = 'D:\\my_project\\python3\\django_project\\ToraOps_project\\ToraOps'
# sys.path.extend([BASE_DIR])
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ToraOps.settings')
# django.setup()

import common.tora_django_common as tdc
import common.vpn_manager as vpnm
import common.common_tools as ct
from myapps.toraapp import models as tmodels
from myapps.tora_monitor import models as mmodels
import logging
logger = logging.getLogger('django')





# def update_django_VpnInfo(engine_room, vpn_user_name, vpn_phone, addr_strs):
#     #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
#     admin_user = tmodels.User.objects.filter(username='admin').first()
#     vpn_info = tdc.get_vpnInfo(engine_room)
#     # if os[:3].lower() == 'win':
#     #     addr_str = inner_ip + '/3389:3389'
#     # else:
#     #     addr_str = inner_ip + '/22:22'
#     vpn_obj, is_created = tmodels.VpnUserInfo.objects.get_or_create(
#                 engine_room=engine_room,
#                 vpn_user_name=vpn_user_name,
#                 defaults={'vpn_address': vpn_info['vpn_address'],
#                           'vpn_user_passwd': vpn_info['vpn_passwd'],
#                           'vpn_phone': vpn_phone,
#                           'server_list': addr_strs,
#                           'operator': admin_user,
#                           'cur_status': '1'})
#     print("is_created:", is_created)
#     if is_created:
#         logger.info("增加vpnuser成功")
#         return 1
#     else:
#         logger.info("vpn记录 %s已存在" % vpn_user_name)
#         if addr_strs != vpn_obj.server_list:
#             vpn_obj.server_list = addr_strs
#             vpn_obj.save()
#             logger.info("更新vpnuser成功")
#             return 1
#         else:
#             logger.info("不需要更新server_list列表")
#             return 1

#获取最新的vpn后台数据，vpn_user,vpn_phone,inner_ip
#custgroup_name没法获取不处理

@ct.async_run
def vpn_data_syn_task():
    try:
        #只同步了金桥机房和东莞机房客户，宛平的vpn不在这里
        vm = vpnm.vpn_manager('dgnf')
        all_user_list = vm.get_user_list()
        print("all_user_list:", all_user_list)
        rec_all = vm.get_resource_list()
        #print(rec_all)
        # for item in rec_all:
        #     print(item['id'], item['name'], item['rctype'])
        
        for vpn_user in all_user_list:
            # if vpn_user['name'] != 'zhangwei':
            #     continue
            print(vpn_user['name'],vpn_user['parent_path'],vpn_user['role_name'])
            if vpn_user['parent_path'] == '/奇点客户/金桥机房':
                engine_room = 'shjq'
            elif vpn_user['parent_path'] == '/奇点客户/南方中心客户':
                engine_room = 'dgnf'
            else:
                engine_room = 'shjq'

            user_data = vm.search_exit_user(vpn_user['name'])
            print(user_data)
            if user_data and user_data['phone'] != '':
                vpn_phone = user_data['phone']
            else:
                vpn_phone = 'None'
            
            role_list = vpn_user['role_name'].split(',')
            role_name_list = []
            for item in role_list :
                if item == 'mac11-bug-虚拟资源':
                    print("不需处理的role_name")
                else:
                    print("需要处理的role_name:", item)
                    role_name_list.append(item)
            print("role_name_list.:", role_name_list)
            recName_list = []
            for role_name in role_name_list:
                role_data = vm.get_role_data_cloud(role_name)
                #print("role_data:", role_data)
                rcId_list = role_data['rcIdsStr'].split(',')
                # print(role_data['rcIdsStr'])
                # print("rcId_list,", rcId_list)
                for id in rcId_list:
                    for item in rec_all:
                        if item['id'] == id and item['rctype'] == '1':
                            #print("item['name'],", item['name'])
                            recName_list.append(item['name'])
            print("资源名字：", vpn_user['name'], role_name, recName_list)
            addr_strs = ''
            for res_name in recName_list:
                res_data = vm.get_rec_data_cloud(res_name)
                print(res_data['addr_str'])
                addr_strs += res_data['addr_str']

            print(vpn_user['name'], vpn_user['note'], engine_room, vpn_phone, addr_strs)
            tdc.update_django_VpnInfo(engine_room, vpn_user['name'], vpn_phone, addr_strs, vpn_user['note'])
        print("执行syn_vpn数据完成！")
        syn_vpn_obj = mmodels.MonitorJob.objects.get(job_id='vpn_syn')
        syn_vpn_obj.last_status = True
        syn_vpn_obj.monitor_data = '执行完成111111'
        syn_vpn_obj.save()
        return 1
    except Exception:
        syn_vpn_obj = mmodels.MonitorJob.objects.get(job_id='vpn_syn')
        syn_vpn_obj.last_status = False
        syn_vpn_obj.monitor_data = '执行异常22222'
        syn_vpn_obj.save()
        return 0


if __name__ == '__main__':
    vpn_data_syn_task()

