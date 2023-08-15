# -*- coding: utf-8 -*-   
  
import os  
import pymysql
import copy
import datetime

scriptpath=os.getcwd()
path_ip=scriptpath+'/SwitchboardData'

db_host="192.168.121.133"
db_user="root"
db_passwd="devops"
# db_host="192.168.10.59"
# db_user="singularity_oper"
# db_passwd="Singularity$20201113"

db_port=3306
db_name="tora_oper_data"
class MySQL(object):
    def __init__(self,host,user,pwd,port,db):
        self.host=host
        self.user=user
        self.passwd=pwd
        self.port=port
        self.db=db

    def GetConnect(self):
        '''
        得到链接信息
        :return:
        '''
        if not self.db:
            raise (NameError,"没有设置数据库信息")
        self.connect=pymysql.connect(host=self.host,user=self.user,passwd=self.passwd,port=self.port,database=self.db,charset="utf8")
        cur=self.connect.cursor()
        if not cur:
            raise (NameError,"链接数据库失败")
        else:
            return cur

    def ExecQuery(self,sql):
        '''
        执行查询语句
        返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段
        '''
        cur=self.GetConnect()
        cur.execute(sql)
        resList = cur.fetchall()

        #查询完毕后必须关闭连接
        self.connect.close()
        return resList

    def ExecNonQuery(self, sql):
        """
        执行非查询语句
        """
        cur = self.GetConnect()
        try:
            cur.execute(sql)
            self.connect.commit()
        except:
            print('执行失败')
        # print('执行成功')
        self.connect.close()

#读取单个文件，返回[{},{},{}]
def zt_read_one_file(file_path):
    results=[]
    with open(file_path, "r") as f:
        for line in f.readlines():
            oneip={"network_ip": '',"network_name": ''}
            line = line.strip('\n')
            data = line.split(',')
            oneip["network_ip"] = data[1]
            oneip["network_name"] = data[0]
            results.append(oneip)
    return results

if __name__ == '__main__':
    ms = MySQL(host=db_host, user=db_user, pwd=db_passwd,port=db_port,db=db_name)
    results = zt_read_one_file(path_ip)
    for oneMachine in results:
        sql="""
        INSERT INTO tora_monitor_networkmonitorip (network_ip,network_name,monitor_flag,send_msg_flag) VALUES ( "{}","{}",1,1);
        """.format(oneMachine["network_ip"],oneMachine["network_name"])
        print(sql)
        ms.ExecNonQuery(sql)