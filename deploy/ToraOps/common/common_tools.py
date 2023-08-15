# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:53:14 2019

@author: zhangwei
"""

import datetime as dt
import time
import os
#import winsound
import smtplib
from email.mime.text import MIMEText
from email.header import Header
#import pyttsx3
import logging
import logging.config
import yaml
import paramiko
import urllib.request as urllib2
import json
# import platform
# sysstr = platform.system()
# if sysstr == 'Linux':
#     import wmi_client_wrapper as wmi
import pandas as pd
#from monitor_server_status import MonitorServer
#import urllib
from threading import Thread



logger = logging.getLogger('main.common_tools')


def write_log(filename, content):
    ntime = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, 'a+') as f:
        f.write(ntime + "::" + content)
        f.write('\n')
        
def write_file(filename, content):
    with open(filename, 'a+') as f:
        f.write(content)
        f.write('\n')
        
def cover_write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
        f.write('\n')
        
def get_server_config(filename):
    result=[]
    try:
        with open(filename, "r") as f:
            for line in f.readlines():
                temp_list = line.split(',')
                temp_list2 = [(str(i).strip()) for i in temp_list]
                result.append(temp_list2)
    except Exception:
        logger.warning("打开文件异常，请确认文件路径是否正确！", exc_info=True)
    return result[1:]

def generate_file(verify_flag, filePrefix): 
    
    if os.path.exists("flag_file"):
        pass
    else:
        os.mkdir('flag_file')
    cur_dir_i = os.getcwd()
    cur_dir = cur_dir_i.replace("\\","/") + "/"   
    flag_file_dir = cur_dir + "flag_file/"
    if os.path.exists(flag_file_dir + filePrefix + '.success'):
        os.remove(flag_file_dir + filePrefix + '.success')
    if os.path.exists(flag_file_dir + filePrefix + '.fail'):
        os.remove(flag_file_dir + filePrefix + '.fail')
    ntime = dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if verify_flag:
        filename = filePrefix + '.success'        
        with open(flag_file_dir + filename, 'a+') as f:
            f.write(ntime + "::" + "monitor success")
            f.write('\n')
    else:
        filename = filePrefix + '.fail'
        with open(flag_file_dir + filename, 'a+') as f:
            f.write(ntime + "::" + "monitor fail")
            f.write('\n')

def time_check(start_time1, end_time1):
#    start_time1 = '09:30'
#    end_time1 = '11:30'
#    start_time2 = '13:00'
#    end_time2 = '15:00'
    now_time = dt.datetime.now().strftime('%H:%M') 
    if (now_time>=start_time1) and (now_time<=end_time1):
        return True
    else:
#        print "now_time is: " + now_time + " It's not Montior time!" 
        return False
    

def trade_check():
    start_time1 = '09:26'
    end_time1 = '11:30'
    start_time2 = '13:01'
    end_time2 = '15:00'
    now_time = dt.datetime.now().strftime('%H:%M')
    if ((now_time>=start_time1) and (now_time<=end_time1)) or ((now_time>=start_time2) and (now_time<=end_time2)):
        return True
    else:
#        print "now_time is: " + now_time + " It's not Montior time!" 
        return False    
    

# def alert_sound():
    
#     duration = 1000  # millisecond
#     freq = 440  # Hz
#     try:
#         for i in range(3):
#             winsound.Beep(freq, duration)
#             time.sleep(1)
#     except Exception as e:
#         print str(e)


# def readTexts(words):
#     try:
#         engine = pyttsx3.init()
#         for i in range(3):
#             engine.say(words)
#             # 注意，没有本句话是没有声音的
#             engine.runAndWait()
#     except Exception as e:
#         print(str(e))


def read_file(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content

        
def send_mail(msg_text, msg_subject):
 
    # 第三方 SMTP 服务
    mail_host="smtp.exmail.qq.com"  #设置服务器
    mail_user="wei.zhang@yrsoft.com.cn"   #用户名
    mail_pass="333333"   #口令
     
     
    sender = 'wei.zhang@yrsoft.com.cn'
    receivers = ['158279489@qq.com'] # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    
    message = MIMEText(msg_text, 'plain', 'utf-8')
    message['From'] = Header("Operator", 'utf-8')
    message['To'] =  Header("Monitor", 'utf-8')
     
    #subject = 'Python SMTP 邮件测试'
    message['Subject'] = Header(msg_subject, 'utf-8')
     
     
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
        print("connected!")
        smtpObj.login(mail_user,mail_pass)
        print("login succeed!")
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("Send mail success!")
    except smtplib.SMTPException as e:
        print("Error: Can't send mail!")
        print(e.args)
        

"""
Setup logging configuration
"""
def setup_logging(default_path, default_level=logging.INFO):
    
    if os.path.exists("./mylog"):
        pass
    else:
        os.mkdir('./mylog')
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        

def getLastWorkDay(nday=dt.datetime.today()):
    
    nday=dt.datetime.today()
    #星期几
    week = int(time.strftime("%w", nday.timetuple()))
    if week == 1:
        interval_day = 3
    else:
        interval_day = 1
    lastWorkDay = (dt.datetime.today()-dt.timedelta(interval_day)).strftime('%Y-%m-%d')
    return lastWorkDay


def getLast2WorkDay(nday=dt.datetime.today()):
    
    #星期几
    week = int(time.strftime("%w", nday.timetuple()))
    if week == 1 or week == 2:
        interval_day = 4
    else:
        interval_day = 2
    last2WorkDay = (dt.datetime.today()-dt.timedelta(interval_day)).strftime('%Y-%m-%d')
    return last2WorkDay

#取上一交易日yyyy-mm-dd
def get_prevTradeDate(theDay):
    this_year = dt.datetime.now().year
    this_year_file = './config/TradeCal_' + str(this_year) + '_SSE.csv'
    df = pd.read_csv(this_year_file,index_col=0)
    prevTradeDate_list = df.loc[df['calendarDate'] == theDay,'prevTradeDate'].values
    if len(prevTradeDate_list) == 0:
        logger.error(" %s 不是交易日" % theDay)
        prevTradeDate = '0000-00-00'
    else:
        prevTradeDate = prevTradeDate_list[0]
        logger.info("上一个交易日为 %s" % prevTradeDate)
    #12月15号的时候检查交易日历文件是否存在，不存在提醒。
    next_year = int(dt.datetime.now().year) + 1
    #next_year = 2020
    next_year_file = './config/TradeCal_' + str(next_year) + '_SSE.csv'
    ndate = dt.datetime.now().strftime("%Y-%m-%d")
    check_date = str(this_year) + "-12-15"
    print("check_date:",check_date)
    if ndate >= check_date:
        logger.info("大于等于12月15号,检查下一年的交易日历文件是否存在")
        if os.path.exists(next_year_file):
            logger.info("交易日历文件存在")
        else:
            msg = "交易日历文件 %s 不存在，请于12月31日前及时获取改配置文件！" % next_year_file
            logger.info(msg)
            send_sms_control('NoLimit',msg)
    else:
        logger.info("小于12月15号，不进行检查。")

    return prevTradeDate


#判断是否是交易日yyyy-mm-dd
def get_isTradeDate(theDay):
    this_year = dt.datetime.now().year
    this_year_file = './config/TradeCal_' + str(this_year) + '_SSE.csv'
    df = pd.read_csv(this_year_file,index_col=0)
    TradeDate_list = df.loc[df['calendarDate'] == theDay]
    if len(TradeDate_list) == 0:
        logger.info(" %s 不是交易日" % theDay)
        flag = False
    else:
        flag = True
        logger.info("%s 是交易日" % theDay)
    #12月15号的时候检查交易日历文件是否存在，不存在提醒。
    next_year = int(dt.datetime.now().year) + 1
    #next_year = 2020
    next_year_file = './config/TradeCal_' + str(next_year) + '_SSE.csv'
    ndate = dt.datetime.now().strftime("%Y-%m-%d")
    check_date = str(this_year) + "-12-15"
    print("check_date:",check_date)
    if ndate >= check_date:
        logger.info("大于等于12月15号,检查下一年的交易日历文件是否存在")
        if os.path.exists(next_year_file):
            logger.info("交易日历文件存在")
        else:
            msg = "交易日历文件 %s 不存在，请于12月31日前及时获取改配置文件！" % next_year_file
            logger.info(msg)
            send_sms_control('NoLimit',msg)
    else:
        logger.info("小于12月15号，不进行检查。")

    return flag


'''
创建 ssh 连接函数
hostip, port, username, password,访问linux的ip，端口，用户名以及密码
'''
def sshConnect(hostip, port, username, password):
    paramiko.util.log_to_file('./mylog/paramiko.log')
    try:
        #创建一个SSH客户端client对象
        sshClient = paramiko.SSHClient()
        # 获取客户端host_keys,默认~/.ssh/known_hosts,非默认路径需指定
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #创建SSH连接
        sshClient.connect(hostip, port, username, password)
        logger.debug("SSH connect success!")
    except Exception as e:
        msg = "SSH connect failed: [hostip:%s];[username:%s];[error:%s]" %(hostip,username,str(e))
#        print msg
        logger.error(msg)
        sshClient = 999
    return sshClient
'''
创建命令执行函数
command 传入linux运行指令
'''
def sshExecCmd(sshClient, command):

    try:
        stdin, stdout, stderr = sshClient.exec_command(command)
    #        if stderr:
    #            stderrstr = stderr.read()
    #            logger.error(u"exec_command error:" + stderrstr.decode('utf-8'))
    #        filesystem_usage = stdout.readlines()
    #        return filesystem_usage
#        stdoutstr = stdout.read()        #pyhon2不需要decode
        stdoutstr = stdout.read().decode('utf-8')
        ssherr = stderr.read().decode('utf-8')
        if ssherr:
            logger.warning("ssh执行命令返回错误：" + ssherr) 
        sshRes = []
        sshRes = stdoutstr.strip().split('\n')
        if sshRes == ['']:
            sshRes = []
    except Exception as e:
        logger.warning(str(e))
        sshRes = []
    return sshRes

'''
关闭ssh
'''
def sshClose(sshClient):
    sshClient.close()
    
    

'''
发送短信,支持多个号码串发送同样的内容。
'''
def fortunesms(message, phone):
    
    logger.debug(phone)
    logger.debug(message)
    count = len(phone.split(','))
    logger.debug(count)
    
    data = r'''<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="
    http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/en
    velope/">
      <soap:Body>
        <MongateCsSpSendSmsNew xmlns="http://tempuri.org/">
                    <userId>HXZQJK</userId>
                    <password>huaxin2019</password>
                    <pszMobis>%s</pszMobis>
                    <pszMsg>%s</pszMsg>
                    <iMobiCount>%d</iMobiCount>
                    <pszSubPort>*</pszSubPort>
            </MongateCsSpSendSmsNew>
      </soap:Body>
    </soap:Envelope>''' % (phone, message, count)
    

    try:
        request = urllib2.Request(
            url='http://10.188.100.240:8082/MWGate/wmgw.asmx',
#            data=data,
            data=data.encode('utf-8'),
            headers={'Content-Type':'application/soap+xml;charset=UTF-8'})
        response = urllib2.urlopen(request)
#        request = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(encoding='UTF8'), headers=headers)
        print("fuuuuu_response", str(response))
        logger.info(str(response))
#        #发送完之后，发送条数回写文件
#        total_count += count
#        No_str = local_date + ',' + str(total_count)
#        with open(sms_no_file, 'a+') as f:
#            f.write(No_str)
#            f.write('\n')
    except urllib2.HTTPError as e:
        logger.warning("sms_HTTPError:" + str(e))
    except urllib2.URLError as e:
        logger.warning("sms_URLError:" + str(e))       
    except Exception as e :
        logger.warning('Send sms unexcepted error occurs ! %s' % str(e))
    else:
        logger.info('Send SMS success!')

'''
启动程序时清理一下表trade_monitor_pare.json，根据日期每天执行一次
'''
def init_sms_control_data():
    
    local_date = dt.datetime.today().strftime('%Y-%m-%d')
    countfile = './config/trade_monitor_para.json'
    with open(countfile, 'r') as f:
        Json_dic = json.load(f)
    if Json_dic["sms_no_control"]["init_day"] != local_date:
        Json_dic["sms_no_control"]["ps_port"] = 0
        Json_dic["sms_no_control"]["mem"] = 0
        Json_dic["sms_no_control"]["fpga"] = 0
        Json_dic["sms_no_control"]["db_init"] = 0
        Json_dic["sms_no_control"]["db_trade"] = 0
        Json_dic["sms_no_control"]["errorLog"] = 0
        Json_dic["sms_no_control"]["ping"] = 0
        Json_dic["sms_no_control"]["disk"] = 0
        Json_dic["sms_no_control"]["core"] = 0
        Json_dic["sms_no_control"]["xwdm"] = 0
        Json_dic["sms_no_control"]["errorID"] = 0
        Json_dic["sms_no_control"]["NoLimit"] = 0
        Json_dic["sms_no_control"]["total_used_count"] = 0
        Json_dic["sms_no_control"]["init_day"] = local_date
        #单项短信发送次数记录清零
        json_str = json.dumps(Json_dic, indent=4)
        with open(countfile, 'w') as json_file:
            json_file.write(json_str)
        logger.debug("Init para data success")
    else:
        #每天只做一次初始化
        logger.debug("Not to init data")
        

'''
短信发送控制，总短信数控制，和单项监控短信控制不超过3次
'''
def send_sms_control(sms_type, msg, phone='13162583883,13681919346,13816703919,18917952875,17512562551,13651808091,17891962350'):
    
#    sms_type='ps_port'
#    msg = 'test'
#    phone='13162583883,13681919346'
    try:
        countfile = './config/trade_monitor_para.json'
        with open(countfile, 'r') as f:
            Json_dic = json.load(f)
            logger.debug(Json_dic)
        total_used_count = Json_dic["sms_no_control"]["total_used_count"]
        total_count = Json_dic["sms_no_control"]["total_count"]
        single_limit = Json_dic["sms_no_control"]["single_limit"]
        total_count = Json_dic["sms_no_control"]["total_count"]
        print("total_count:", total_count)
    except Exception as e:
        print("发送异常")
        print(str(e))
##    sms_type = "NoLimi1t"
#    if sms_type == "NoLimit":
#        single_times = 0
#    else:
#        try:
#            single_times = Json_dic["sms_no_control"][sms_type]
#        except Exception as e:
#            logger.error(str(e))
#            single_times = 999
    try:
        single_times = Json_dic["sms_no_control"][sms_type]
    except Exception as e:
        logger.warning(str(e))
        single_times = 999    
    if sms_type == "NoLimit":
        #NoLimit不限制
        single_times = 0
    logger.info("单项已发送短信次数：%d" % single_times)
    logger.info("已发送短信总条数：%d" % total_used_count)
    #小于限制时才允许发送短信
    if single_times != 999 and total_used_count < total_count and single_times < single_limit:
        message = "【奇点监控】" + msg
        fortunesms(message, phone)
        #发送后增加已发送的次数
        count = len(phone.split(','))
        Json_dic["sms_no_control"]["total_used_count"] = total_used_count + count
        Json_dic["sms_no_control"][sms_type] = single_times + 1
        
        json_str = json.dumps(Json_dic, indent=4)
        with open(countfile, 'w') as json_file:
            json_file.write(json_str)
    else:
        logger.error("已超过当天可发送的短信总数：%d 条" % total_count)
        


'''
支持发送短信开关
item='status'查看状态
item=0关闭
item=N,N>0,表示打开发送功能，并设置短信总数=N，开始默认是100
'''
def sms_switch(item):
    
    countfile = './config/trade_monitor_para.json'
    with open(countfile, 'r') as f:
        Json_dic = json.load(f)
        logger.debug(Json_dic)
    total_used_count = Json_dic["sms_no_control"]["total_used_count"]
    total_count = Json_dic["sms_no_control"]["total_count"]
    
    if item == 'status':
        if total_count > 0 :
            logger.info("已启用发送短信，当天短信总数限制为： %d, 已发送总数为： %d" % (total_count, total_used_count))
        else:
            logger.info("已关闭发送短信")
    elif item >= 0:
        Json_dic["sms_no_control"]["total_count"] = item        
        json_str = json.dumps(Json_dic, indent=4)
        with open(countfile, 'w') as json_file:
            json_file.write(json_str)
        logger.info("已设置当天短信总数限制为： %d" % item)
    else:
        logger.warning("输入不正确，必须为'status'或者大于等于0的整数")
        
        
'''
获取windows远程系统的OS信息。
'''
# def get_remote_windows_os_info(username, password, hostip):
#     try:
#         wmic = wmi.WmiClientWrapper(username, password, hostip)
#         output = wmic.query("SELECT * FROM Win32_OperatingSystem")
#         caption = output[0]["Caption"]
#     except Exception as e:
#         msg = "连接远程windows系统[%s]异常" % hostip
#         logger.error(msg, exc_info=True)
#         #print("error:",str(e))
#         caption = "Null"
#     return caption


# #公用task任务
# def common_monitor_task(task, single_handle, linuxInfo):
    
#     try:
#         ms = MonitorServer(linuxInfo, single_handle)
#         task_monitor = ms.single_common_monitor
        
#         task_monitor()
#         check_result_list = ms.common_Check_flag_list
#         if len(check_result_list)==0:
#             check_result =False
#         else:
#             check_result = (sum(check_result_list)==len(check_result_list))
# #        print "check_result: ", check_result
#     except Exception as e:
#         check_result = False
#         msg = str(e)
#         logger.warning(msg)

#     if check_result:
#         logger.info("All Server is OK")
#     else:
#         msg = task + "::" + single_handle + " 任务监控报警，请检查详细日志内容！"
#         logger.warning(msg)
# #        ct.send_sms_control("disk", msg)
#         sysstr = platform.system()
#         if sysstr == "Windows":
#             readTexts("Monitor task is Worning")

#获取远程的文件大小 
def get_remote_filesize(sshClient, filepath):

#    command = 'du -h ' + remote_dir + '/2019-06-12*'
    command = 'du -sh ' + filepath
    logger.info(command)
    stdin,stdout,stderr = sshClient.exec_command(command)
#        stdoutstr = stdout.read()    #python2.7不需要decode
    stdoutstr = stdout.read().decode('utf-8')
    logger.debug(stdoutstr)
#        print("leng:", stderr)
#            stderrstr = stderr.read()      #python2.7不需要decode
    stderrstr = stderr.read().decode('utf-8')
    if stderrstr:
        logger.error(u"exec_command error:" + stderrstr)
        return '0'
    sshRes = []
    sshRes = stdoutstr.strip().split('\n')
#        print "sshRes:", sshRes    
    filesize = sshRes[0].split('\t')[0]
    return filesize


def async_run(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


class MyThread(Thread):

    def __init__(self,func,args,name=''):
        Thread.__init__(self)
        self.name=name
        self.func=func
        self.args=args
    
    def run(self):
        #python3不支持apply
#        apply(self.func,self.args)
        self.result = self.func(*self.args)
        
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

def get_remote_ssh_command_data(hostip, username, password, command, port=22):
    
    #logger = logging.getLogger()
    # yaml_path = './config/non_trade_monitor_logger.yaml'
    # ct.setup_logging(yaml_path)

    sshClient = sshConnect(hostip, port, username, password)
    sshRes = sshExecCmd(sshClient, command)
    logger.info(hostip + "::" + command)
    sshResList = []
    print("sshRes:", type(sshRes),sshRes)
    try:
        for item in sshRes:
#                de_item = item.decode('gb2312')
#                error_list = de_item.strip().split(':', 1)
#                grep_lists.append(error_list)
#                memstr=','.join(error_list)
#                print memstr
#                temstr= item.strip().encode('utf-8')
            temstr = item.strip()
            sshResList.append(temstr)
            logger.info(temstr)
        return sshResList
    except Exception as e:
        msg = "write failed: [hostip:%s];[username:%s];[error:%s]" % (hostip,username,str(e))
        logger.error(msg)
        return None

    finally:    
        sshClose(sshClient)
        logger.info("get_ssh_command_data finished")
        for handler in logger.handlers:
            logger.removeHandler(handler)
