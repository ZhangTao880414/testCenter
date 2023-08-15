#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   vpn_manager.py
@Time    :   2021/04/08 09:39:37
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib
import requests
import time
import os
# sha256加密
import hashlib
# 忽略https证书验证的警告
import urllib3
import datetime
import configparser
import logging


logger = logging.getLogger('django')
urllib3.disable_warnings()



class vpn_manager:

    def __init__(self, engine_room):
        path = os.getcwd()
        filename = os.path.join(path,'config/vpn_config.cfg')
        #filename = './config/vpn_config.cfg'
        print("filename:", filename)
        #self.engine_room = engine_room
        self.cf = configparser.ConfigParser()
        self.cf.read(filename, encoding='utf-8')
        if engine_room == 'shwp':
            self.base_url = self.cf.get("url_param","WP_base_url")
            self.vpn_key = self.cf.get("passwd","wp_vpn_key")
        else:
            self.base_url = self.cf.get("url_param","NQSZ_base_url")
            self.vpn_key = self.cf.get("passwd","jq_vpn_key")
        print("self.vpn_key:", self.vpn_key)
        # 设置请求头
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'charset': 'UTF-8'
        }
        

        # 新建用户需要的信息
        #self.name = ''
        #self.init_passwd = self.cf.get("passwd","vpn_init_pw") #不用了20210630
        self.parent_group = self.cf.get("parent_group",engine_room)
        #self.phone = ''
        self.gqsj = 0
        now_time = datetime.datetime.now() + datetime.timedelta(days=365)
        self.ex_time = now_time.strftime('%Y-%m-%d')
        #self.user_note = '自动创建'

        # 新建资源需要的信息
        #self.rec_name = ''
        #self.addr_str = ''
        self.rctype = 1  # TCP资源
        self.note = ''
        self.rc_grp_name = self.cf.get("rc_grp_name", engine_room)

    # Helper Function
    # 根据不同url的param返回请求主体中的data字符串
    def get_token_data(self, url_param, url_param_data, timestamp):

        # 拼接api含有的param和请求体的params，但未改变url_param_data_Adduser
        #print("url_paramqqq:", url_param)
        url_param.update(url_param_data)
        query_string = self.create_param(url_param)
        # sha256加密拼接的字符串
        sinfor_apitoken = self.get_sinfor_apitoken(query_string, url_param_data, timestamp)
        data = 'sinfor_apitoken=' + sinfor_apitoken

        return data


    # 将字符串解析为字典
    def resol_url_param(self, url_string):
        url_param = {}
        lt = str(url_string).split('&')
        for i in lt:
            llt = str(i).split('=')
            url_param[llt[0]] = llt[1]
        return url_param


    # 封装一个request方法，便于各个API接口调用
    def get_request(self, url, data):
        req_url = self.base_url + url
        res = requests.post(req_url, data=data.encode('utf8'), verify=False, headers=self.headers)
        return res


    def get_sinfor_apitoken(self, query_string, request_param, timestamp):
        # 传入的是query_string
        # 需要手动拼接一下待加密的字符串
        sha256_param = query_string + str(timestamp) + self.vpn_key
        #print('-------加密字段', sha256_param)

        sha256 = hashlib.sha256(sha256_param.encode('utf8'))
        # 拼接apiToken字段
        tokenlt = []
        tokenlt.append(str(sha256.hexdigest()))
        for i in request_param:
            tokenlt.append(i + '=' + str(request_param[i]))
        sinfor_apitoken = '&'.join(tokenlt)
        return sinfor_apitoken


    # 用于排序param，返回拼接好的字段
    def create_param(self, param):
        lt = []
        # 对params排序
        for i in sorted(param):
            lt.append(i+'='+str(param[i]))
        query_string = '&'.join(lt)
        # 使用& 拼接querystring
        return query_string

    #查询vpn用户是否存在
    def search_exit_user(self, username):
        # 是否存在用户
        exist_user = False
        timestamp = int(time.time())
        search_user_url_path = self.cf.get("url_param","ex_get_user_Info")
        url_param = self.resol_url_param(search_user_url_path)
        url_param_search_user = {
            'timestamp': timestamp,
            'username': username
            #'id': username
        }
        url_param.update(url_param_search_user)
        data = self.get_token_data(url_param, url_param_search_user, timestamp)
        #print('-------Search User----', data)
        res = self.get_request(search_user_url_path, data)
        res_dict = res.json()
        #print("res_dict:", res_dict)    
        if res.json().get('code') == 0:
            #exist_user = True
            user_data = res_dict['result']
            #print('----------存在同名用户-----------')
            return user_data
        return exist_user

    #增加新用户
    def add_new_user(self, name, phone, vpn_init_passwd, custgroup_name):
        # 获取秒级时间戳
        timestamp = int(time.time())
        # 计算params
        # 获取url中的原始参数
        add_user_url = self.cf.get("url_param","add_User_Cloud")
        url_param = self.resol_url_param(add_user_url)
        # 获取不同请求接口需要放入body中的参数
        url_param_data_Adduser = {
            'timestamp': timestamp,
            'name': name,
            'passwd': vpn_init_passwd,
            'parent_group': self.parent_group,
            'phone': phone,
            'gqsj': self.gqsj,
            'ex_time': self.ex_time,
            'note': custgroup_name
        }
        data = self.get_token_data(url_param, url_param_data_Adduser, timestamp)
        print('-------add New User----', data)

        #add_new_user_url_path = url_path_param.add_User_Cloud.get('url_param')
        add_new_user_url_path = self.cf.get("url_param", "add_User_Cloud")
        # 调用封装的request
        res = self.get_request(add_new_user_url_path, data)
        #print(res.text)
        res_dict = res.json()
        print("新建资源返回", res_dict)
        logger.info(str(res_dict))
        return res_dict['code']


    #编辑用户
    def update_user_note_cloud(self, old_name, new_name, parent_group, new_note):
        # 获取秒级时间戳
        timestamp = int(time.time())
        # 计算params
        # 获取url中的原始参数
        update_user_url = self.cf.get("url_param","update_user_cloud")
        url_param = self.resol_url_param(update_user_url)
        # 获取不同请求接口需要放入body中的参数
        url_param_data_updateuser = {
            'timestamp': timestamp,
            'old_name': old_name,
            'new_name': new_name,
            'parent_group': parent_group,
            'note': new_note
            #'b_inherit_auth': 0
        }
        data = self.get_token_data(url_param, url_param_data_updateuser, timestamp)
        print('-------update User----', data)
        # 调用封装的request
        res = self.get_request(update_user_url, data)
        #print(res.text)
        res_dict = res.json()
        print("更新用户返回", res_dict)
        logger.info(str(res_dict))
        return res_dict['code']


    #查询用户列表, offset:获取用户信息起始位置,默认0
    def get_user_list(self, offset=0):

        timestamp = int(time.time())
        get_user_list_url = self.cf.get("url_param","get_user_list")
        url_param = self.resol_url_param(get_user_list_url)
        url_param_data_get_user_list = {
            'timestamp': timestamp,
            'offset': offset,
            'limit': 1000
        }
        data = self.get_token_data(url_param, url_param_data_get_user_list, timestamp)
        res = self.get_request(get_user_list_url, data)
        print("查询返回", type(res), res)
        res_dict = res.json()
        print("客户列表查询返回", res_dict)
        if res_dict['code'] == 0:
            print("user数量：", len(res_dict['result']['data']))
            return res_dict['result']['data']
        else:
            logger.error("api查询异常，没有返回结果！")
            return []



    #查询资源列表
    def get_resource_list(self):
        timestamp = int(time.time())
        get_rec_list_url = self.cf.get("url_param","get_resource_list")
        url_param = self.resol_url_param(get_rec_list_url)
        url_param_data_get_rec_list = {
            'timestamp': timestamp,
            'limit': 9999
        }
        data = self.get_token_data(url_param, url_param_data_get_rec_list, timestamp)
        res = self.get_request(get_rec_list_url, data)
        #print("授权查询返回", type(res), res)
        res_dict = res.json()
        #print("资源列表查询返回", res_dict)
        if res_dict['code'] == 0:
            print(len(res_dict['result']['data']))
            return res_dict['result']['data']
        else:
            logger.error("api查询异常，没有返回结果！")
            return []

    #查询资源是否存在,res_name=inner_ip
    def get_rec_data_cloud(self, res_name):
        exist_res = False
        timestamp = int(time.time())
        get_rec_data_url = self.cf.get("url_param","get_rec_data_cloud")
        url_param = self.resol_url_param(get_rec_data_url)

        url_param_data_get_rec = {
            'timestamp': timestamp,
            'name': res_name
        }

        data = self.get_token_data(url_param, url_param_data_get_rec, timestamp)
        res = self.get_request(get_rec_data_url, data)
        res_dict = res.json()
        print(res_dict)
        if res.json().get('code') == 0:
            exist_rec = True
            #rec_id = res_dict['result']['id']
            res_data = res_dict['result']
            print('存在资源:%s' % res_name)
            return res_data
        return exist_res

    #新建资源
    def add_new_rec(self, inner_ip, os):
        timestamp = int(time.time())
        add_new_rec_url = self.cf.get("url_param","add_Res_Cloud")
        url_param = self.resol_url_param(add_new_rec_url)
        if os[:3].lower() == 'win':
            addr_str = inner_ip + '/3389:3389'
        else:
            addr_str = inner_ip + '/22:22'

        url_param_data_new_rec = {
            'timestamp': timestamp,
            'name': inner_ip,
            'addr_str': addr_str,
            'rctype': self.rctype,
            'note': self.note,
            'rc_grp_name': self.rc_grp_name
        }

        data = self.get_token_data(url_param, url_param_data_new_rec, timestamp)
        res = self.get_request(add_new_rec_url, data)
        #print(res.text)
        res_dict = res.json()
        #print("新建资源返回", res_dict)
        return res_dict['code']

    #删除资源        
    def delete_rec_cloud(self, inner_ip):
        pass


    #查询用户的角色授权情况, 根据role_name(inner_ip)查询
    def get_role_data_cloud(self, role_name):
        exist_role = False
        timestamp = int(time.time())
        get_role_data_url = self.cf.get("url_param","get_role_data_cloud")
        url_param = self.resol_url_param(get_role_data_url)
        #role_name = self.cf.get("role_name_prefix", self.engine_room) + custgroup_name
        #role_name = inner_ip
        url_param_data_get_role = {
            'timestamp': timestamp,
            'name': role_name
        }
        data = self.get_token_data(url_param, url_param_data_get_role, timestamp)
        res = self.get_request(get_role_data_url, data)
        #print("授权查询返回", type(res), res)
        res_dict = res.json()
        #print("授权查询返回", res_dict)
        if res_dict['code'] == 0:
            res_data = {}
            #exist_role = True
            res_data['role_id'] = res_dict['result']['id']
            res_data['userIdsStr'] = res_dict['result']['userIdsStr']
            res_data['rcIdsStr'] = res_dict['result']['rcIdsStr']
            res_data['userNames'] = res_dict['result']['userNames']
            #print(res_dict['result']['userIdsStr'],res_data['userNames'],res_dict['result']['rcIdsStr'])
            print('存在角色:%s' % role_name)
            # user_list = res_data['userNames'].split(',')
            # if vpn_name in user_list:
            #     print("vpn用户%s已经有该角色：%s 的权限" % (vpn_name, role_name))
            # else:
            #     print("vpn用户%s已经没有该角色：%s 的权限" % (vpn_name, role_name))
            return res_data
        return exist_role

    #新建角色，即新建立用户和资源的对应关系
    def add_role_cloud(self, custgroup_name, vpn_name, inner_ip):
        timestamp = int(time.time())
        add_new_auth_role_url = self.cf.get("url_param","add_new_auth_role")
        url_param = self.resol_url_param(add_new_auth_role_url)
        #role_name = self.cf.get("role_name_prefix", self.engine_room) + custgroup_name
        role_name = inner_ip
        url_param_data_add_role = {
            'timestamp': timestamp,
            'name': role_name,
            'rcNamesStr': inner_ip,
            'userNamesStr': vpn_name
        }
        data = self.get_token_data(url_param, url_param_data_add_role, timestamp)
        
        res = self.get_request(add_new_auth_role_url, data)
        print('------授权用户：', vpn_name, '---资源名称：', inner_ip)
        #print(res.text)
        res_dict = res.json()
        print("新建角色返回", res_dict)
        return res_dict['code']

    #更新角色，即新建立用户和资源的对应关系
    def update_role_cloud(self, custgroup_name, vpn_name, inner_ip, add_flag):
        timestamp = int(time.time())
        role_data = self.get_role_data_cloud(inner_ip)
        update_role_cloud_url = self.cf.get("url_param","update_role_cloud")
        url_param = self.resol_url_param(update_role_cloud_url)
        #role_name = self.cf.get("role_name_prefix", self.engine_room) + custgroup_name
        role_name = inner_ip
        user_list = role_data['userNames'].split(',')
        userId_list = role_data['userIdsStr'].split(',')
        rcId_list = role_data['rcIdsStr'].split(',')
        rec_all = self.get_resource_list()
        recName_list = []
        for id in rcId_list:
            for item in rec_all:
                if item['id'] == id:
                    recName_list.append(item['name'])
        print("recName_list:", recName_list)
        all_user_list = self.get_user_list()
        username_list = []
        for userId in userId_list:
            for user in all_user_list:
                if int(user['id']) == int(userId):
                    username_list.append(user['name'])
                    break
        userNamesStr = ','.join(username_list)
        #增加
        if add_flag:
            if inner_ip not in recName_list:
                rcNamesStr = inner_ip + ',' + ','.join(recName_list)
            else:
                rcNamesStr = ','.join(recName_list)

            
            if vpn_name not in username_list:
                userNamesStr += ',' + vpn_name
            else:
                print("vpn_name:%s已经存在角色授权里了" % vpn_name)
        #删除
        else:
            if inner_ip in recName_list:
                recName_list.remove(inner_ip)
                rcNamesStr = ','.join(recName_list)
            else:
                rcNamesStr = ','.join(recName_list)

            if vpn_name in username_list:
                username_list.remove(vpn_name)
                userNamesStr = ','.join(username_list)
            else:
                print("vpn_name:%s已经不在角色授权里了" % vpn_name)
        #'userIdsStr': '43,44', 'rcIdsStr': '88',
        # rcNamesStr = '192.168.10.59,192.168.10.214'
        print("update_userNamesStr:", userNamesStr)
        url_param_data_update_role = {
            'timestamp': timestamp,
            'oldName': role_name,
            'newName': role_name,
            'rcNamesStr': rcNamesStr,
            'userNamesStr': userNamesStr
        }
        data = self.get_token_data(url_param, url_param_data_update_role, timestamp)
        res = self.get_request(update_role_cloud_url, data)
        # print('------更新角色：', role_name, '用户：', vpn_name, '---资源名称：', inner_ip)
        # print(res.text)
        res_dict = res.json()
        print("更新角色返回", res_dict)
        return res_dict['code']





def test():
    inner_ip = '192.168.10.111'
    os = 'Centos'
    vpn_name = 'zhangwei'
    custgroup_name = '张伟组'
    vm = vpn_manager('dgnf')
    # res_user = vm.search_exit_user(vpn_name)
    # print(res_user)
    # query_rec = vm.get_rec_data_cloud(inner_ip)
    # if query_rec == False:
    #     res_add_rec = vm.add_new_rec(inner_ip, os)
    #     if res_add_rec == 0:
    #         print("增加资源成功")
    #     else:
    #         print("增加资源失败")
    # else:
    #     print("资源已存在！")
    # query_role = vm.get_role_data_cloud('张伟组','zhangwei')
    # if query_role == False:
    #     print('role不存在，需新增')
    # else:
    #     print("role存在，更新role的用户和资源权限")
    #     vm.update_role_cloud(zhangwei, inner_ip)
    # update_role = vm.update_role_cloud(custgroup_name, vpn_name, inner_ip)


    user_list = vm.get_user_list()
    rec_all = vm.get_resource_list()
    #print(rec_all)
    # for item in rec_all:
    #     print(item['id'], item['name'], item['rctype'])
    
    for vpn_user in user_list:
        # if vpn_user['name'] != 'zhangwei':
        #     continue
        print(vpn_user['name'],vpn_user['parent_path'],vpn_user['role_name'])
        if vpn_user['parent_path'] == '/奇点客户/宁桥路客户':
            engine_room = 'shnq'
        elif vpn_user['parent_path'] == '/奇点客户/南方中心客户':
            engine_room = 'dgnf'
        else:
            engine_room = 'shnq'
        user_data = vm.search_exit_user(vpn_user['name'])
        print(user_data)
        if user_data:
            vpn_phone = user_data['phone']
        else:
            vpn_phone = 'none'
        
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
            print("role_data:", role_data)
            rcId_list = role_data['rcIdsStr'].split(',')
            print(role_data['rcIdsStr'])
            print("rcId_list,", rcId_list)
            for id in rcId_list:
                for item in rec_all:
                    #print("item['id']",type(id),type(item['id']),type(item['rctype']),item['id'] == id,item['rctype'] == 1)
                    if item['id'] == id and item['rctype'] == '1':
                        print("item['name'],", item['name'])
                        recName_list.append(item['name'])
        print("资源名字：", vpn_user['name'], role_name, recName_list)
        addr_strs = ''
        for res_name in recName_list:
            res_data = vm.get_rec_data_cloud(res_name)
            print(res_data['addr_str'])
            addr_strs += res_data['addr_str']

        print(vpn_user['name'], engine_room, vpn_phone, addr_strs)
        print("call tdc task")
                # addr_str_tem = res_data['addr_str'].replace(",", "\n")
                # print(addr_str_tem)
                
            

    #vm.get_resource_list()
    # print("res:", res_user, res_rec, res_role)

def testadd():
    vpn_user_name = 'test_zw'
    vpn_phone = '12345678901'
    custgroup_name = '张伟组2'
    vm = vpn_manager('shnq')
    res_code = vm.add_new_user(vpn_user_name, vpn_phone, 'hxzq123',custgroup_name)
    print("res_code:", res_code)

def testupdate():
    vpn_user_name = 'zhangwei2'
    vpn_phone = '13386168061'
    #parent_group = '/证书认证-海外客户/中微'
    parent_group = '/奇点网络运维'
    custgroup_name = '张伟20210729'
    vm = vpn_manager('shnq')
    res_code = vm.update_user_note_cloud(vpn_user_name, vpn_user_name, parent_group, custgroup_name)
    print("res_code:", res_code)


def update_all_user_note():
    vm = vpn_manager('shjq')
    all_user_list = vm.get_user_list()
    import pandas as pd
    pddata = pd.read_csv('./config/shjq_vpn.csv', encoding='utf-8')
    print(pddata)
    errorList = []
    empty_note_users = []
    for vpn_user in all_user_list:

        user_data = vm.search_exit_user(vpn_user['name'])
        #print(user_data)
        if user_data and user_data['phone'] != '':
            vpn_phone = user_data['phone']
        else:
            vpn_phone = 'Not not not not not phone'
        vpn_note = None
        for row in pddata.itertuples():
            # os = getattr(row, 'os')
            # old_inner_ip = getattr(row, 'inner_ip')
            custgroup_name = getattr(row, 'cust_group')
            vpns = getattr(row, 'vpns')
            vpn_list = vpns.split(';')
            #print(vpn_user['name'], vpn_list, vpn_user['name'] in vpn_list)
            if vpn_user['name'] in vpn_list:
                vpn_note = custgroup_name
                break
        if vpn_note == None:
            vpn_note = 'Anonymous_' + vpn_user['name']
            empty_note_users.append(vpn_user['name'])
        print(vpn_user['name'],vpn_user['parent_path'],vpn_phone, vpn_note )
        res_code = vm.update_user_note_cloud(vpn_user['name'], vpn_user['name'], vpn_user['parent_path'], vpn_note)
        #print("res_code:", res_code)
        if res_code != 0:
            errorList.append(vpn_user['name'])
    print("empty_users:", empty_note_users)
    print("error_users:", errorList)
        

if __name__ == "__main__":
    #testupdate()
    #update_all_user_note()
    # import pandas as pd
    # pddata = pd.read_csv('shjq_vpn.csv', encoding='utf-8')
    # print(pddata)
    # for row in pddata.itertuples():
    #     # os = getattr(row, 'os')
    #     # old_inner_ip = getattr(row, 'inner_ip')
    #     custgroup_name = getattr(row, 'cust_group')
    #     vpns = getattr(row, 'vpns')
    #     vpn_list = vpns.split(';')
    #     print('cust:', custgroup_name, vpn_list)
    vm = vpn_manager('shwp')
    all_user_list = vm.get_user_list()
    print("all_user_list:", all_user_list)
    #testadd()
    # for i in [1,2,3,4,5]:
    #     if i not in[1,4]:
    #         continue
    #     print(i)