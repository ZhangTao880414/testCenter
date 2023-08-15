#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   Ops_console.py
@Time    :   2020/07/13 17:50:41
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib


import argparse
import sys
import mssql_tools as mt
import common_tools as ct
import logging
import logging.config
import yaml
import datetime as dt
import time
import os
import pandas as pd
import process_shcfg as psh


logger = logging.getLogger()

#固定参数
#tora_hxzq_dir = "E:\\tora\\hxzq\\"
tora_hxzq_dir = "D:\\env_chb\\"
#节点配置信息
node_config_csv = 'D:\\my_project\\python3\\django_project\\ToraOps_project\\ToraOps\\common\\csv\\node_config.csv'
#备份服务器信息
back_server_csv = 'D:\\my_project\\python3\\django_project\\ToraOps_project\\ToraOps\\common\\csv\\back_server_info.csv'
#服务器信息
servers_csv = 'D:\\my_project\\python3\\django_project\\ToraOps_project\\ToraOps\\common\\csv\\servers_info.csv'
#python2启动命令
cmd_py2 = "D:\\env_chb\\env\\Scripts\\activate.bat && "


class tora_node():
    #version = None
    def __init__(self, node_id, components, version): 
        self.node_id = node_id
        self.componentList = components
        self.node_name = self.get_node_name()
        print("self.node_name:",self.node_name)
        self.version = version
        self.cfg_dir = tora_hxzq_dir + self.version + '\\cfg\\' + self.node_name + '\\cfg\\'
        #self.sh_cfg_file = self.cfg_dir + 'sh.cfg'
        self.sql_update_dir = tora_hxzq_dir + self.version + '\\cfg\\' + self.node_name + '\\update\\'
        self.DBInsert_cfg_file = self.sql_update_dir + 'bulk_insert_update_list.csv'
        self.stop_command = self.generate_tora_command('StopService')
        self.db_init_command = self.generate_tora_command('DBInit')
        self.clean_command = self.generate_tora_command('Clean')
        self.copy_command = self.generate_tora_command('CopyAll')
        self.start_command = self.generate_tora_command('StartService')
        self.show_command = self.generate_tora_command('Show')
        self.insert_command = self.generate_tora_command('DBInsert -l ' + self.DBInsert_cfg_file)
        print("self.show_command",self.show_command)
        #self.show_command = "python D:\env_chb\3.9.1\Console.py -H D:\env_chb\3.9.1 -N hx_InnerTest -c Show"
        self.db_export_command = self.generate_tora_command('DBCsvExport')

    #奇点命令行生成
    def generate_tora_command(self,comm):
        command = cmd_py2 + "python " + tora_hxzq_dir + self.version + "\\Console.py -H " + tora_hxzq_dir + self.version + " -N " + self.node_name + " -c " + comm
        return command

    #get node_name by node_id
    def get_node_name(self):
        df = pd.read_csv(node_config_csv,index_col=None)
        pieces = df.loc[df['node_id'] == int(self.node_id)]
        print(pieces)
        if len(pieces) != 0:
            name_list = list(pieces['node_name'])
            node_name = name_list[0]
        else:
            logger.error("节点%s没有配置记录" % str(self.node_id))
            node_name = None
        return node_name

    #获取数据库升级目录下的所有sql文件
    def get_update_sql_files(self):
        sql_files = []
        if os.path.exists(self.sql_update_dir):
            files = os.listdir(self.sql_update_dir)
            for filename in files:
                if '.sql' in filename:
                    sql_files.append(os.path.join(self.sql_update_dir,filename))
        return sql_files


    #根据字段值关联csv文件取得切片,类似select * from table where condition
    #value必须同时为单值，或者list
    def get_csv_pieces(self, csv_file, column1, value1, column2=None, value2=None):
        df = pd.read_csv(csv_file,index_col=None)
        if column2 == None:
            if type(value1) == list:
                pieces = df.loc[df[column1].isin(value1)]
            else:
                pieces = df.loc[df[column1] == value1]
        else:
            if (type(value1) == list) & (type(value2) == list):
                pieces = df.loc[df[column1].isin(value1) & df[column2].isin(value2)]
            elif (type(value1) == list) | (type(value2) == list):
                logger.error("value不能只有一个是list,一个是值")
            else:
                pieces = df.loc[(df[column1] == value1) & (df[column2] == value2)]
        return pieces


    #根据节点获取要备份的服务器IP信息
    def get_back_servers(self):
        print("self.node_id:",self.node_id)
        bs_pieces = self.get_csv_pieces(back_server_csv, 'node_id', int(self.node_id))
        print("bs_pieces:",bs_pieces)
        server_ip_list = list(bs_pieces['server_ip'])
        #for ip in server_ip_list:
        servers_pieces = self.get_csv_pieces(servers_csv,'in_ip',server_ip_list)
        print("servers_pieces:",servers_pieces)
        return servers_pieces

    #更新奇点版本号
    def update_tora_version(self,update_version):
        try:
            node_df = pd.read_csv(node_config_csv,index_col=None)
            for index_s, row_s in node_df.iterrows():
                if str(row_s['node_id']) == self.node_id:
                    node_df.loc[index_s,'last_version'] = update_version
                    node_df.loc[index_s,'upgrade_time'] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            node_df.to_csv(node_config_csv, index=False, encoding='utf-8')
            return 1
        except Exception:
            logger.error('Error,更新奇点版本失败', exc_info=True)
            return 0

    #取上一次节点升级的版本号，即当前版本
    def get_last_version(self):
        node_df = pd.read_csv(node_config_csv,index_col=None)
        last_version = None
        for index_s, row_s in node_df.iterrows():
            if row_s['node_id'] == self.node_id:
                last_version = node_df.loc[index_s,'last_version']
                return last_version
        return last_version      

    #获取mssql配置信息
    def get_mssqldb_info(self):
        #sh_cfg_file = 'D:\\work\\auto_update\\tora_package\\hx_wanping\\cfg\\sh.cfg'
        #sh_cfg_file = tora_hxzq_dir + self.node_name + '\\cfg\\sh.cfg'
        sh_cfg_file = self.cfg_dir + 'sh.cfg'
        pfg = psh.process_shcfg(sh_cfg_file)
        info = pfg.get_mssql_info()
        server = info["DB_IP"]
        user = info["DB_USER"]
        #password = info["DB_PASSWD"]
        password = "adminadmin$3"
        dbname = info["DB_NAME"]
        upload_dbname = info["DOWNLOAD_DB_NAME"]
        mssqldb_info = [server, user, password, dbname, upload_dbname]
        print("mssqldb_info:",mssqldb_info)
        return mssqldb_info

    #备份mssql数据库
    def backup_mssql_db(self):
        mssqldb_info = self.get_mssqldb_info()
        #登陆只需要传入1个dbname
        db_info = mssqldb_info[:4]
        (cursor, conn) = mt.connect_mssql(db_info)
        server = mssqldb_info[0]
        dbname = mssqldb_info[3]
        upload_dbname = mssqldb_info[4]
        if cursor != None:    
            #执行备份
            back_list = []
            backdb_files = []
            for db_item in [dbname, upload_dbname]:
                ntimes = dt.datetime.now().strftime("%Y%m%d%H%M%S")
                back_file = "C:\Backup_DataBase\{0}_{1}.bak".format(db_item, ntimes)
                sql1 = '''declare @path nvarchar(256)
                        set @path = 'C:\Backup_DataBase\{0}_{1}.bak'
                        backup database [{0}] to disk = @path with format '''.format(db_item, ntimes)
                logger.info("sql:" + sql1)
                conn.autocommit(True)
                try:
                    cursor.execute(sql1)
                    # res1 = None
                    # errmsg = 'executed statement has no resultset'
                    # logger.info("res1:")
                    # logger.info(res1)
                    back_list.append(1)
                    backdb_files.append(back_file)
                    logger.info("执行服务器%s备份数据库 %s 成功" % (server,db_item))
                except Exception as e:
                    logger.error('sql 执行异常', exc_info=True)
                    errmsg = str(e)
                    # res1 = None
                    logger.error("errmsg:" + errmsg)
                    logger.info("Error,执行服务器%s备份数据库 %s 失败" % (server,db_item))
                    back_list.append(0)
                conn.autocommit(False)             
            conn.close()
            logger.info(back_list)
        else:
            logger.error("连接数据库失败")
            # flag = False
        return backdb_files  

    #执行sql文件到mssql
    def execute_sql_from_file(self, cursor, conn, sql_file):
        try:
            mssqldb_info = self.get_mssqldb_info()
            #登陆只需要传入1个dbname
            db_info = mssqldb_info[:4]
            (cursor, conn) = mt.connect_mssql(db_info)
            # db_info = ['192.168.238.10', 'sa', '123.comA', 'test_upload']
            # (cursor, conn) = mt.connect_mssql(db_info)
            with open(sql_file, 'r', encoding='gb2312') as f:
                # 读取整个sql文件，以分号切割。[:-1]删除最后一个元素，也就是空字符串
                sql_list = f.read().split(';')[:-1]
                for x in sql_list:
                    # 判断包含空行的
                    if '\n' in x:
                        # 替换空行为1个空格
                        x = x.replace('\n', ' ')
                    # 判断多个空格时
                    if '    ' in x:
                        # 替换为空
                        x = x.replace('    ', '')
                    # sql语句添加分号结尾
                    sql_item = x + ';'
                    # print(sql_item)
                    conn.autocommit(True)
                    cursor.execute(sql_item)
                    #c.execute(sql_item)
                    logger.info("执行成功的sql语句: %s" % sql_item)
            logger.info('执行sql脚本文件%s升级脚本完成' % sql_file)
            excute_flag = 1              
        except Exception as e:
            print(e)
            logger.error('Error,执行sql脚本文件%s升级脚本失败' % sql_file)
            excute_flag = 0

        return excute_flag

    #升级mssql数据库脚本
    def upgrade_mssql_db(self):
        try:
            mssqldb_info = self.get_mssqldb_info()
            #登陆只需要传入1个dbname
            db_info = mssqldb_info[:4]
            (cursor, conn) = mt.connect_mssql(db_info)
            # db_info = ['192.168.238.10', 'sa', '123.comA', 'test_upload']
            # (cursor, conn) = mt.connect_mssql(db_info)
            sql_files = self.get_update_sql_files()
            if sql_files != []:
                check_list = []
                for sql_file in sql_files:
                    res = self.execute_sql_from_file(cursor, conn, sql_file)
                    check_list.append(res)
                if sum(check_list) == len(check_list):
                    logger.info("节点%s升级数据库sql脚本成功" % self.node_name)
                    upgrade_flag = 1
                else:
                    logger.error("节点%s升级数据库sql脚本有执行未成功的记录" % self.node_name)
                    upgrade_flag = 0
            else:
                logger.info("sql脚本文件为空，不需要升级数据库")
                upgrade_flag = 1
                
        except Exception as e:
            logger.error(str(e))
            logger.error('Error,节点 %s升级mssql数据库脚本失败' % self.node_name)
            upgrade_flag = 0
        finally:
            # 关闭mssql连接
            conn.autocommit(False)
            conn.close()
            return upgrade_flag


    #备份节点run目录和数据库，传入节点和当前的版本号
    def backup_tora(self):
        #返回字典,AuthDeviceSerial.csv的备份IP和路径，以及备份数据库名字
        res_dict = {'authserver':[],'back_db':[]}
        #根据node解析到需要备份的服务器IP,和用户，密码等信息
        back_servers = self.get_back_servers()
        logger.info("back_servers:")
        logger.info(back_servers)
        #stop server
        res_stop = os.system(self.stop_command)
        logger.info("res_stop:")
        logger.info(res_stop)
        #执行Show
        show_status = self.show_tora()
        logger.info("show_status:" + str(show_status))
        if show_status != 0 :
           logger.error('节点有进程没有offline，停止备份和后续升级')
           return 0
        #DBInit
        res_init = os.system(self.db_init_command)
        #res_init = os.popen(self.db_init_command).readlines()
        logger.info("res_init:")
        logger.info(res_init)
        #DBCsvExport
        res_export = os.system(self.db_export_command)
        #res_export = os.popen(self.db_export_command).readlines()
        logger.info("res_export:")
        logger.info(res_export)
        #Clean
        res_clean = os.system(self.clean_command)
        #res_clean = os.popen(self.clean_command).readlines()
        logger.info("res_clean:")
        logger.info(res_clean)
        #取上一次系统版本号
        b_version = self.get_last_version()
        #没有指定版本号就用日期时间字符串代替
        if b_version == None:
            b_version = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_back_dir = '/home/trade/run_' + b_version
        #根据节点，连接到对应服务器，备份run目录。默认备份目录是run_{时间}，可指定版本号备份-v {version},run_{version}
        for index, row in back_servers.iterrows():
            hostip = row['in_ip']
            port = 22
            username = row['normal_user']
            password = str(row['normal_passwd'])
            #远程备份run目录
            sshClient = ct.sshConnect(hostip,port,username,password)
            back_com = 'cp -r run run_' + b_version
            res = sshClient.exec_command(back_com)
            print("excute_commd_res:", res)
            ct.sshClose(sshClient)
            
            #更新back_server.csv的last_back_dir,back_time
            bk_df = pd.read_csv(back_server_csv,index_col=None)
            for index_s, row_s in bk_df.iterrows():
                if row_s['server_ip'] == row['in_ip']:
                    bk_df.loc[index_s,'last_back_dir'] = 'run_' + b_version
                    bk_df.loc[index_s,'back_time'] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bk_df.to_csv(back_server_csv, index=False, encoding='utf-8')

        #取得authserver机器的IP和备份目录
        server_csv = self.cfg_dir + 'server.csv'
        IP_values = ct.get_csv_fields(server_csv,'IP','server','authserver')
        serviceno_values = ct.get_csv_fields(server_csv,'serviceno','server','authserver')
        AuthDeviceSerial_back_path = run_back_dir + 'authserver' + str(serviceno_values[0]) + '/csv/AuthDeviceSerial.csv'
        res_dict["authserver"] = [IP_values[0], AuthDeviceSerial_back_path]
        #备份数据库
        backdb_files = self.backup_mssql_db()
        if len(backdb_files) == 2:
            logger.info("ok,节点[%s]数据库备份成功,备份文件为：%s" % (self.node_id, ";".join(backdb_files)))
        else:
            logger.error("error,[%s]数据库备份失败" % self.node_id)

        res_dict["back_db"] = backdb_files

        return res_dict


    #还原节点程序，传入节点和要还原的版本号（上次备份的目录）
    def restore_tora(self, r_version):
        #根据node解析到需要备份的服务器IP,和用户，密码等信息
        back_servers = self.get_back_servers()
        #stop server
        res_stop = os.system(self.stop_command)
        #执行Show
        show_status = self.show_tora()
        logger.info("show_status:" + str(show_status))
        if show_status != 0 :
           logger.error('节点有进程没有offline，停止还原')
           return 0
        #DBInit
        res_init = os.system(self.db_init_command)
        #Clean
        res_clean = os.system(self.clean_command)
        #根据节点，连接到对应服务器，备份run目录。默认备份目录是run_{时间}，可指定版本号备份-v {version},run_{version}
        error_list = []
        for index, row in back_servers.iterrows():
            hostip = row['in_ip']
            port = 22
            username = row['normal_user']
            password = str(row['normal_passwd'])
            #远程备份run目录
            try:
                sshClient = ct.sshConnect(hostip,port,username,password)
                restore_com = 'mv run run_del & cp -r ' + r_version + ' run'
                res = sshClient.exec_command(restore_com)
                print("excute_commd_res:", res)
     
            except Exception:
                logger.error('Faild to mv the run files!', exc_info=True)
                error_list.append(hostip)
            finally:
                ct.sshClose(sshClient)
        
            # #还原版本应该更新node_config.csv的版本号last_version,upgrade_time
            # node_df = pd.read_csv(node_config_csv,index_col=None)
            # for index_s, row_s in node_df.iterrows():
            #     if row_s['server_ip'] == row['in_ip']:
            #         node_df.loc[index_s,'last_version'] = r_version
            #         node_df.loc[index_s,'upgrade_time'] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # node_df.to_csv(node_config_csv, index=False, encoding='utf-8')
            if len(error_list) == 0:
                logger.info("节点%s还原成功" % str(self.node_id))
                self.update_tora_version(r_version)
            else:
                logger.error("节点%s还原失败" % str(self.node_id))
                logger.error(error_list)
        #还原数据库
        print("restore database")
        #执行StartService
        res_start = os.system(self.start_command)
        if res_start != 0:
            logger.error("启动节点[%s]服务程序异常！" % self.node_id)
        #执行Show
        res_show = os.popen(self.show_command).readlines()
        print("res_show:", res_show)
        show_status = self.show_tora()
        if show_status:
            logger.info("节点 %s show正常" % self.node_id)
        else:
            logger.error("Error，节点 %s show异常" % self.node_id)


    #根据节点名称，show当前系统的运行状态
    def show_tora(self):
        #执行Show
        #res_show = os.system(self.show_command)
        res_show = os.popen(self.show_command).readlines()
        #解析最后一列是否是正常
        logger.info("res_show:")
        logger.info(res_show)
        sshResStr = ''.join(res_show)
        sshResList = sshResStr.strip().split('\n')
        #print(len(sshResList))
        check_list = []
        for sshCom in sshResList:
            #sshResLists.append(sshCom.strip().split())
            tt = 'offline' not in sshCom
            #print(tt)
            check_list.append(tt)
        logger.info(check_list)
        #正常状态的话，更新一下节点系统状态为运行状态
        if sum(check_list) == len(check_list):
            logger.info("节点%s运行正常" % self.node_id)
            show_status = 1
        #0表示所有的都是offline
        elif sum(check_list) == 0:
            logger.error("Error，节点%s运行异常，所有进程offline" % self.node_id)
            show_status = 0
        else:
            logger.error("Error，节点%s运行异常,有进程offline" % self.node_id)
            show_status = 2
        node_df = pd.read_csv(node_config_csv,index_col=None)
        #if show_status == 1:
        #运行正常,更新node_config.sys_status
        #node_pieces = self.get_csv_pieces(node_config_csv, 'node_id', self.node_id)
        for index_s, row_s in node_df.iterrows():
            print("row_s['node_id']:",type(row_s['node_id']),type( self.node_id))
            if str(row_s['node_id']) == self.node_id:
                node_df.loc[index_s,'sys_status'] = str(show_status)
                node_df.loc[index_s,'monitor_time'] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(node_df)
        node_df.to_csv(node_config_csv, index=False, encoding='utf-8')

        return show_status

    #升级系统
    def upgrade_tora(self):
        return 1
        #备份run目录和数据库
        back_dict = self.backup_tora()
        if back_dict == 0:
            logger.error("执行备份失败，停止升级！")
            return 0
        logger.info(back_dict)
        #执行Insert
        res_Insert = os.system(self.insert_command)
        logger.info("res_Insert:")
        logger.info(res_Insert)
        #执行CopyAll
        #res_CopyAll = os.system(self.copy_command)
        res_CopyAll = os.popen(self.copy_command).readlines()
        logger.info("res_CopyAll:")
        logger.info(res_CopyAll)
        #还原AuthDeviceSerial.csv文件
        #auth_csv_info = back_dict["authserver"]
        backdb_info = back_dict["back_db"]
        authserver_ip = back_dict["authserver"][0]
        auth_csv_bk_path = back_dict["authserver"][1]
        #取得authserver机器的IP和备份目录
        server_csv = self.cfg_dir + 'server.csv'
        serviceno_values = ct.get_csv_fields(server_csv,'serviceno','server','authserver')
        auth_csv_dir = '/home/trade/' + 'authserver' + str(serviceno_values[0]) + '/csv/'
  
        port = 22
        username = 'trade'
        password = '123456'
        sshClient = ct.sshConnect(authserver_ip,port,username,password)
        restore_com = 'cp ' + auth_csv_bk_path + ' ' + auth_csv_dir
        res = sshClient.exec_command(restore_com)
        logger.info("excute_commd_res:")
        logger.info(res)
        ct.sshClose(sshClient)
        #升级数据库
        print("升级数据库")
        upgrade_db_flag = self.upgrade_mssql_db()
        logger.info("升级数据库状态:" + str(upgrade_db_flag))
        #执行StartService
        res_start = os.system(self.start_command)
        logger.info("res_start:")
        logger.info(res_start)
        # if res_start != 0:
        #     logger.error("启动节点[%s]服务程序异常！" % self.node_id)
        #执行Show
        show_status = self.show_tora()
        logger.info("show_status:" + str(show_status))
        if show_status == 1:
            logger.info("节点[%s]show正常" % self.node_id)
            return 1
        else:
            logger.error("Error，节点 %s show异常" % self.node_id)
            return 0
        #升级成功，则更新节点的版本号
        self.update_tora_version(self.version)
        #升级成功则再置成关闭状态，StopService, DBInit,Clean(手工做)
     

    #部署新环境节点
    def deploy_tora(self):
        
        #指定节点和版本号,部署新环境
        #获得新节点需要初始化环境的服务器IP等信息
        #redhat系统环境设置，安装rpm包，bash_profile,数据库配置
        #升级数据库（手工）
        #执行CopyAll
        #执行StartService
        #执行Show
        #升级成功，则更新节点的版本号
        pass

    #test
    def test(self):
        #指定节点和版本号
        # #stop server
        # res_stop = os.system(self.stop_command)
        # #DBInit
        # res_init = os.system(self.db_init_command)
        # #DBCsvExport
        # res_export = os.system(self.db_export_command)
        #备份数据库
        ##back_flag = self.backup_mssql_db()
        ##if back_flag:
        ##    logger.info("ok,节点[%s]数据库备份成功" % self.node_id)
        ##else:
        ##    logger.error("error,[%s]数据库备份失败" % self.node_id)
        # #Clean
        # res_clean = os.system(self.clean_command)
        # #执行CopyAll
        # res_CopyAll = os.system(self.copy_command)
        #升级数据库
        back_dict = self.backup_tora()
        print("升级数据库11111")
        ##upgrade_db_flag = self.upgrade_mssql_db()
        ##print("upgrade_db_flag:",upgrade_db_flag)
        # #执行StartService
        # res_start = os.system(self.start_command)
        # if res_start != 0:
        #     logger.error("启动节点[%s]服务程序异常！" % self.node_id)
        # #执行Show
        # show_status = self.show_tora()
        # if show_status:
        #     logger.info("节点[%s]show正常" % self.node_id)
        # else:
        #     logger.error("Error，节点 %s show异常" % self.node_id)
        # #升级成功，则更新节点的版本号
        # self.update_tora_version(self.version)
        #升级成功则再置成关闭状态，StopService, DBInit,Clean(手工做)


def run():

    try:
        yaml_path = './config/ops_console_logger.yaml'
        ct.setup_logging(yaml_path)

        parser = argparse.ArgumentParser()

        #parser.add_argument('text', help = 'print some text')
        # parser.add_argument('-v','--value', nargs = 2, type = int, help = 'the sum of 2 int')
        # parser.add_argument('--sparse', action='store_true', default=False, help='GAT with sparse version or not.')
        # parser.add_argument('--seed', type=int, default=72, help='Random seed.')
        parser.add_argument('-t','--task', help='指定任务类型：backup;restore;upgrade;show')
        parser.add_argument('-n','--node', help='指定节点编号')
        parser.add_argument('-v','--version', help='指定版本')
        parser.add_argument('-s','--server', nargs='*', help='指定服务器IP地址')
        parser.add_argument('-c','--component', help='指定组件')

        args = parser.parse_args()
        #mysql DATETIME格式
        ntime = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("ntime:",ntime)
        Infos = ct.get_server_config(servers_csv)
        for info in Infos:
            print("info:",info)


        # 输出两个部分
        print("任务:", args.task)

        print("args:", args)
        print("input server:", args.server, type(args.server))

        # if args.value:
        #     print(args.value[0]+args.value[1])
        print((args.node,args.version))
        node = tora_node(args.node,args.version)

        if args.task == 'backup':
            print("do backup")
            #stop server
            #DBInit
            #Clean
            #根据节点，连接到对应服务器，备份run目录。默认备份目录是run_{时间}，可指定版本号备份-v {version},run_{version}
            back_dict = node.backup_tora()
            #备份数据库
            if back_dict != 0:
                logger.info("节点%s备份成功" % (args.node))
            else:
                logger.info("节点%s备份失败" % (args.node))

        elif args.task == 'restore':
            print("do restore")
            #还原指定的版本号，恢复程序run目录到备份的程序
            #还原数据库
            #执行StartService
            #执行Show
            node.restore_tora(args.version)
        elif args.task == 'upgrade':
            print("do upgrade")
            #指定节点和版本号
            #备份数据库
            #stop server
            #DBInit
            #Clean
            #执行CopyAll
            #升级数据库
            #执行StartService
            #执行Show
            #升级成功，则更新节点的版本号
            #升级成功则再置成关闭状态，StopService, DBInit,Clean(手工做)
            res = node.upgrade_tora()
            #node.test()
            if res == 1:
                logger.info("节点%s升级成功" % (args.node))
            else:
                logger.error("节点%s升级失败" % (args.node))
        elif args.task == 'deploy':
            print("do new deploy")
            #指定节点和版本号,部署新环境
            #redhat系统环境设置，安装rpm包，bash_profile
            #升级数据库（手工）
            #执行CopyAll
            #执行StartService
            #执行Show
            #升级成功，则更新节点的版本号
        elif args.task == 'show':
            #print("do show")
            #if args.server == None:
                #print("show all node status")
                #显示当前节点的状态信息和版本号
                # node_df = pd.read_csv(node_config_csv,index_col=None)
                # node_list = node_df.node_id
                # for node in node_list:
                #     status = node.show_tora(node)
                #     print('show server: %s status %s' % (node,status))
            #else:
            show_status = node.show_tora()
            logger.info('节点: %s 运行状态 %s' % (args.node,status))
            if show_status == 1:
                logger.info("ok,节点[%s]show正常" % args.node)
            else:
                logger.error("Error，节点[%s]show异常" % args.node)
        else:
            logger.error("-t 参数任务项输入有误！")

    except Exception:
        logger.error('Faild to run ops_console!', exc_info=True)
    finally:
        for handler in logger.handlers:
            logger.removeHandler(handler)

if __name__ == '__main__':
    print("sys.arg:",sys.argv[1:])
    if sys.argv[1:] == []:
        print("请输入对应的参数。输入参数 [-h] 查看帮助文档")
        sys.exit()
    run()