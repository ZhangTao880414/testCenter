#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   vpn_auto_setting.py
@Time    :   2021/05/28 10:51:17
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib

import pandas as pd
import logging
import time
import vpn_manager as vm



logger = logging.getLogger()

def update_shjq_vpn_setting():

    pddata = pd.read_csv('./config/vpn_setting_0718.csv', encoding='gbk')
    #如果有过滤参数'is_monitor'，则过滤需要监控的记录
    pd_columns = pddata.columns.values.tolist()
    #print("pdata:", pddata)
    for row in pddata.itertuples():
        os = getattr(row, 'os')
        old_inner_ip = getattr(row, 'inner_ip')
        n_inner_ip = getattr(row, 'n_inner_ip')
        vpns = getattr(row, 'vpn')
        vpn_list = vpns.split(';')
        #print("vpn_len:", n_inner_ip, len(vpn_list))
        #print(os)
        vma = vm.vpn_manager('shjq')
        exist_rec = vma.get_rec_data_cloud(n_inner_ip)
        if not exist_rec:
            vma.add_new_rec(n_inner_ip, os)
            
        for vpn_name in vpn_list:
            exist_user = vma.search_exit_user(vpn_name)
            print("exist_user:", vpn_name, exist_user)
            if exist_user:
                pass
            else:
                print("-------------vpn_name: %s 不存在----------------！" % vpn_name)
            exist_role = vma.get_role_data_cloud(n_inner_ip)
            print("exist_role:", exist_role)
            if exist_role :
                #存在角色
                vma.update_role_cloud('gourp_name', vpn_name, n_inner_ip, 1)
            else:
                vma.add_role_cloud('group_name', vpn_name, n_inner_ip)

#update_shjq_vpn_setting()
pddata = pd.read_csv('cust_machine_0805.csv', encoding='gbk',keep_default_na=False)
pd_columns = pddata.columns.values.tolist()
print(pd_columns)
# for item in pd_columns:
    # code_str = "%s = getattr(row, '%s')" % (item, item)
    # print(code_str)
# for row in pddata.itertuples():
#     engine_room = getattr(row, 'engine_room')
#     assert_number = getattr(row, 'assert_number')
#     assert_type = getattr(row, 'assert_type')
#     cabinet = getattr(row, 'cabinet')
#     unit = getattr(row, 'unit')
#     model = getattr(row, 'model')
#     serial_number = getattr(row, 'serial_number')
#     IT_checked_number = getattr(row, 'IT_checked_number')
#     configuration = getattr(row, 'configuration')
#     node_name = getattr(row, 'node_name')
#     use_status = getattr(row, 'use_status')
#     opertaion_system = getattr(row, 'opertaion_system')
#     inner_ip = getattr(row, 'inner_ip')
#     outer_ip = getattr(row, 'outer_ip')
#     high_trade_ip = getattr(row, 'high_trade_ip')
#     high_mqA_ip = getattr(row, 'high_mqA_ip')
#     high_mqB_ip = getattr(row, 'high_mqB_ip')
#     ipmi_ip = getattr(row, 'ipmi_ip')
#     note = getattr(row, 'note')
#     disk_serial = getattr(row, 'disk_serial_number')
#     custgroup_name = getattr(row, 'custgroup_name')
#     shelf_time = getattr(row, 'shelf_time')
#     buyer = getattr(row, 'buyer')
#     comment = getattr(row, 'comment')
#     #print(opertaion_system, shelf_time,node_name,buyer,custgroup_name)
#     os ='no_os'
#     os_version = 'no_version'
#     for os_item in ['redhat','centos','ubuntu','windows','clear linux','clearos','gentoo','arch linux','debian']:
#         i = len(os_item)
#         #print(i, opertaion_system[:6].lower())
#         if opertaion_system[:i].lower() == os_item:
#             os = os_item
#             os_version = opertaion_system[i:].strip()          
#             continue
    
#     if os == 'no_os':
#         os = opertaion_system
#         if os == '':
#             os = 'not sure'
#     #print(os, os_version)
#     #print(custgroup_name, buyer)
#     #print(shelf_time,node_name)
#     node_no = node_name.split('号节点')[0]
#     #print(node_no)
#     if shelf_time == '老' or shelf_time == '':
#         shelf_date = '2018-01-01'
#     else:
#         #shelf_date = time.mktime(time.strptime(shelf_time, "%Y年%M月%d日"))
#         date_str = shelf_time.replace('年','-').replace('月','-').replace('日','')
#         #print(date_str)
#         date_list = date_str.split('-')
#         if len(date_list[1]) == 1:
#             mm = '0' + date_list[1]
#         else:
#             mm = date_list[1]
#         if len(date_list[2]) == 1:
#             dd = '0' + date_list[2]
#         else:
#             dd = date_list[2]
#         shelf_date = '%s-%s-%s' % (date_list[0], mm, dd)
#     #print(shelf_date)
#     #print(use_status, buyer)
#     #cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
#     # if buyer == '客户自购':
#     #     cust_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name=custgroup_name).first()
#     #     owner_obj = cust_obj
#     # elif buyer == '华鑫采购':
#     #     hxzq_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='华鑫证券').first()
#     #     owner_obj = hxzq_obj
#     # else:
#     #     qckj_obj =  tmodels.ToraCustomer.objects.filter(custgroup_name='全创科技').first()
#     #     owner_obj = qckj_obj
#     purpose = '1'
#     if model:
#         band_models = model.split()
#         server_brand = band_models[0]
#         server_model = model
#     else:
#         server_brand = 'None'
#         server_model = 'None'
#     #print(server_brand)

#     if not serial_number :
#         serial_number = 'None'
    
    #print(serial_number)
    #print(inner_ip,outer_ip,high_trade_ip,high_mqA_ip,high_mqB_ip,ipmi_ip)

tem = '/home/trade/rtt/date/sp/20210811/4/SZSEkernel_rtt.csv'
print(tem.split('/')[-4])

