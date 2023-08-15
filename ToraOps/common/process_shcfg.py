#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   process_shcfg.py
@Time    :   2020/08/20 09:44:30
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib
import configparser


class process_shcfg:

    def __init__(self,filename):

        self.filename =  filename
        #self.filename = 'D:\\work\\auto_update\\tora_package\\hx_wanping\\cfg\\sh.cfg'
        print("self.filename:",self.filename)
        #  实例化configParser对象
        self.cf = configparser.ConfigParser()
        self.cf.read(self.filename)
        print(self.cf.sections())

    # #  定义方法，获取config分组下指定name的值
    # def getConfigValue(self, name):
    #     value = self.cf.get("config", name)
    #     return value
    # #  定义方法，获取cmd分组下指定name的值
    # def getCmdValue(self, name):
    #     value = self.cf.get("cmd", name)
    #     return value

# sh_cfg_file = 'D:\\work\\auto_update\\tora_package\\hx_wanping\\cfg\\sh.cfg'
# cf = configparser.ConfigParser()
# cf.read(sh_cfg_file)
        #获取mssql数据库信息
    def get_mssql_info(self):
        db_info = {}
        db_info['DB_IP'] = self.cf.get("DB","DB_IP")
        db_info['DB_USER'] = self.cf.get("DB","DB_USER")
        db_info['DB_PASSWD'] = self.cf.get("DB","DB_PASSWD")
        db_info['DB_NAME'] = self.cf.get("DB","DB_NAME")
        db_info['DOWNLOAD_DB_NAME'] = self.cf.get("DB","DOWNLOAD_DB_NAME")
        return db_info



def test():
    sh_cfg_file = 'D:\\work\\auto_update\\tora_package\\hx_wanping\\cfg\\sh.cfg'

    psh = process_shcfg(sh_cfg_file)
    info = psh.get_mssql_info()
    server = info["DB_IP"]
    user = info["DB_USER"]
    password = info["DB_PASSWD"]
    password = "adminadmin\$8"
    dbname = info["DB_NAME"]
    upload_dbname = info["DOWNLOAD_DB_NAME"]
    db_info = [server, user, password, dbname]
    print("db_info:",db_info)


if __name__ == "__main__":
    test()