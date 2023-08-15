# -*- coding: utf-8 -*-   
  
import os  
import pymysql
import copy


local_file_dir='C:\workspaces\devops\ipmiinfo'
db_host="172.19.48.2"
db_user="root"
db_passwd="devops"
db_port=3306
db_name="tora_oper_data"
basemodel={"ipmi_ip":'', "cpu1": 0, "cpu2": 0, "cpu3": 0, "cpu4": 0,
    "fan1": 0, "fan2": 0, "fan3": 0, "fan4": 0, "fan5": 0, "fan6": 0, "fan7": 0, "fan8": 0, "fan9": 0, "fan10": 0, "fan11": 0, "fan12": 0, "fan13": 0, "fan14": 0, "fan15": 0, "fan16": 0, "check_time":'', "baseline_flag": 0, "origin_data": ''}

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
    time = ''
    results=[]
    mydata=[]
    with open(file_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            mydata.append(line)
    time=mydata[0]
    cpulist=[]
    fanlist=[]
    one_machine_info={}
    flag=0
    origin_data = ''
    origin_data_flag=0
    for item in mydata:
        if item == '---' and flag == 0:
            cpulist=[]
            fanlist=[]
            origin_data = ''
            one_machine_info=copy.deepcopy(basemodel)
            flag=1
            continue
        if flag == 1:
            if 'ip' in item and origin_data_flag==0:
                one_machine_info["ipmi_ip"]=item.split(":")[1]
            elif 'degrees' in item and origin_data_flag==0:
                temp=item.split("|")[1]
                cpulist.append(temp)
            elif ('rpm' in item or 'percent' in item) and origin_data_flag==0:
                fansp=item.split("|")[1]
                if 'percent' in item:
                    fansp=int(float(fansp)*7200/100)
                fanlist.append(fansp)
            elif '--' == item and origin_data_flag==0:
                origin_data_flag=1
            elif '--' == item and origin_data_flag==1:
                origin_data_flag=0
            elif origin_data_flag==1:
                origin_data = origin_data +item +";"
            elif item == '---':
                cpulist.sort(reverse=True)
                fanlist.sort(reverse=True)
                for cputemp in cpulist:
                    if one_machine_info["cpu1"] == 0:
                        one_machine_info["cpu1"]=cputemp
                    elif one_machine_info["cpu2"] == 0:
                        one_machine_info["cpu2"]=cputemp
                    elif one_machine_info["cpu3"] == 0:
                        one_machine_info["cpu3"]=cputemp
                    elif one_machine_info["cpu4"] == 0:
                        one_machine_info["cpu4"]=cputemp
                    else:
                        pass
                for onefan in fanlist:
                    if one_machine_info["fan1"] == 0:
                        one_machine_info["fan1"]=onefan
                    elif  one_machine_info["fan2"]==0:
                        one_machine_info["fan2"]=onefan
                    elif  one_machine_info["fan3"]==0:
                        one_machine_info["fan3"]=onefan
                    elif  one_machine_info["fan4"]==0:
                        one_machine_info["fan4"]=onefan
                    elif  one_machine_info["fan5"]==0:
                        one_machine_info["fan5"]=onefan
                    elif  one_machine_info["fan6"]==0:
                        one_machine_info["fan6"]=onefan
                    elif  one_machine_info["fan7"]==0:
                        one_machine_info["fan7"]=onefan
                    elif  one_machine_info["fan8"]==0:
                        one_machine_info["fan8"]=onefan
                    elif  one_machine_info["fan9"]==0:
                        one_machine_info["fan9"]=onefan
                    elif  one_machine_info["fan10"]==0:
                        one_machine_info["fan10"]=onefan
                    elif  one_machine_info["fan11"]==0:
                        one_machine_info["fan11"]=onefan
                    elif  one_machine_info["fan12"]==0:
                        one_machine_info["fan12"]=onefan
                    elif  one_machine_info["fan13"]==0:
                        one_machine_info["fan13"]=onefan
                    elif  one_machine_info["fan14"]==0:
                        one_machine_info["fan14"]=onefan
                    elif  one_machine_info["fan15"]==0:
                        one_machine_info["fan15"]=onefan
                    elif  one_machine_info["fan16"]==0:
                        one_machine_info["fan16"]=onefan
                one_machine_info["check_time"]=time
                one_machine_info["origin_data"] = origin_data
                results.append(one_machine_info)
                flag=0
    return results

if __name__ == '__main__':
    # sql = """
    # SELECT * FROM tora_monitor_ipmiinfodata;
    # """
    ms = MSSQL(host=db_host, user=db_user, pwd=db_passwd,port=db_port,db=db_name)
    allFiles=zt_get_file_list(local_file_dir)
    for oneFile in allFiles:
        print(oneFile)
        results = zt_read_one_file(oneFile)
        for oneMachine in results:
            sql="""
            INSERT INTO tora_monitor_ipmiinfodata ( ipmi_ip, cpu1_temp,cpu2_temp,cpu3_temp,cpu4_temp,fan1_sp,fan2_sp,fan3_sp,fan4_sp,fan5_sp,fan6_sp,fan7_sp,fan8_sp,fan9_sp,fan10_sp,fan11_sp,fan12_sp,fan13_sp,fan14_sp,fan15_sp,fan16_sp,check_time,baseline_flag,origin_data) VALUES ( "{}",{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},"{}",{},"{}");
            """.format(oneMachine["ipmi_ip"],oneMachine["cpu1"],oneMachine["cpu2"],oneMachine["cpu3"],oneMachine["cpu4"],oneMachine["fan1"],oneMachine["fan2"],oneMachine["fan3"],oneMachine["fan4"],oneMachine["fan5"],oneMachine["fan6"],oneMachine["fan7"],oneMachine["fan8"],oneMachine["fan9"],oneMachine["fan10"],oneMachine["fan11"],oneMachine["fan12"],oneMachine["fan13"],oneMachine["fan14"],oneMachine["fan15"],oneMachine["fan16"],oneMachine["check_time"],oneMachine["baseline_flag"],oneMachine["origin_data"])
            # print(sql)
            ms.ExecNonQuery(sql)