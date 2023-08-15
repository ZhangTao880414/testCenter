# -*- coding: utf-8 -*-   
  
import os  
import pymysql
import copy


local_file_dir='C:\workspaces\devops'
db_host="172.19.48.2"
db_user="root"
db_passwd="devops"
db_port=3306
db_name="tora_oper_data"
basemodel={"ipmi_ip":''}

class MSSQL(object):
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

#获取文件列表
def zt_get_file_list(file_dir):   
    fileLists=[]   
    for root, dirs, files in os.walk(file_dir):  
        for file in files:  
            if os.path.splitext(file)[1] == '.txt':  
                fileLists.append(os.path.join(root, file))  
    return fileLists

#读取单个文件，返回[{},{},{}]
def zt_read_one_file(file_path):
    results=[]
    with open(file_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            results.append(line)
    return results

if __name__ == '__main__':
    # sql = """
    # SELECT * FROM tora_monitor_ipmiinfodata;
    # """
    ms = MSSQL(host=db_host, user=db_user, pwd=db_passwd,port=db_port,db=db_name)
    # allFiles=zt_get_file_list(local_file_dir)
    oneFile = "C:\workspaces\devops\ip"
    results = zt_read_one_file(oneFile)
    for ip in results:
        sql="""
        INSERT INTO tora_monitor_ipmimonitorip (ipmi_ip) VALUES ( "{}");
        """.format(ip)
        print(sql)
        ms.ExecNonQuery(sql)
