#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import mdapi
import logging
import common.common_tools as ct
import getopt
import json
import datetime as dt
import time
import pandas as pd
import csv
import threading

logger = logging.getLogger()


class MdSpi(mdapi.CTORATstpMdSpi):
    def __init__(self,api, CheckData):
        mdapi.CTORATstpMdSpi.__init__(self)
        self.__api=api
        self.__req_id=1
        self.SubscribeList = CheckData['SubscribeMarketData']
        self.QuriyList = CheckData['QuiryMarketData']
        self.__address = CheckData['address']
        self.login_flag = False

    def auto_increase_reqid(self):
        self.__req_id = self.__req_id + 1

    def OnFrontConnected(self):
        logger.info("OnFrontConnected")
        #请求登录
        login_req = mdapi.CTORATstpReqUserLoginField()
        self.__api.ReqUserLogin(login_req,self.__req_id) 

    def OnRspUserLogin(self, pRspUserLoginField, pRspInfo, nRequestID, bIsLast):
        logger.info("OnRspUserLogin: ErrorID[%d] ErrorMsg[%s] RequestID[%d] IsLast[%d]" % (pRspInfo['ErrorID'], pRspInfo['ErrorMsg'], nRequestID, bIsLast))
        # #订阅行情
        # if pRspInfo['ErrorID'] == 0:
        #     sub_list=[b'000000']
        #     self.__api.SubscribeMarketData(sub_list, mdapi.TORA_TSTP_EXD_COMM)
        #test
        print("call login resp", pRspInfo['ErrorID'])
        if pRspInfo['ErrorID'] == 0:
            self.login_flag = True
            for list_dict in self.SubscribeList:
                encode_str = list_dict["SecurityID"].encode('utf-8')
                #ExchangeID = list_dict["ExchangeID"]
                if list_dict["ExchangeID"] == 'SSE':
                    ExchangeID = mdapi.TORA_TSTP_EXD_SSE
                elif list_dict["ExchangeID"] == 'SZSE':
                    ExchangeID = mdapi.TORA_TSTP_EXD_SZSE
                elif list_dict["ExchangeID"] == 'HK':
                    ExchangeID = mdapi.TORA_TSTP_EXD_HK
                else:
                    ExchangeID = mdapi.TORA_TSTP_EXD_COMM

                #订阅行情要交易所分开订阅    
                sub_list=[]
                sub_list.append(encode_str)

                #sub_list=[b'000001']
                logger.info("sublist:")
                logger.info(sub_list)
                res = self.__api.SubscribeMarketData(sub_list, ExchangeID)
                print("订阅返回：", res)

            

    def OnRspSubMarketData(self, pSpecificSecurity, pRspInfo, nRequestID, bIsLast):
        logger.info("OnRspSubMarketData")
        logger.info(pSpecificSecurity)
        logger.info(pRspInfo)


    def OnRtnDepthMarketData(self, pDepthMarketData):
#        pass
        #print("pDepthMarketData:::", pDepthMarketData)

        logger.info("OnRtnDepthMarketData SecurityID[%s] TradingDay[%s] LastPrice[%.2f] Volume[%d] Turnover[%.2f] BidPrice1[%.2f] BidVolume1[%d] AskPrice1[%.2f] AskVolume1[%d] UpdateTime[%s]" % (pDepthMarketData['SecurityID'],
                                                                    pDepthMarketData['TradingDay'],
                                                                    pDepthMarketData['LastPrice'],
                                                                    pDepthMarketData['Volume'],
                                                                    pDepthMarketData['Turnover'],
                                                                    pDepthMarketData['BidPrice1'],
                                                                    pDepthMarketData['BidVolume1'],
                                                                    pDepthMarketData['AskPrice1'],
                                                                    pDepthMarketData['AskVolume1'],
                                                                    pDepthMarketData['UpdateTime']))
        nowtime = dt.datetime.now()
        UpdateTime = dt.datetime.strptime(pDepthMarketData['UpdateTime'], '%H:%M:%S')
        delta = nowtime - UpdateTime
        print("行情和本机时间差:", delta.seconds, pDepthMarketData['SecurityID'])
        diff = 0
        if delta.seconds > 600:
            diff = delta.seconds - 86400
        else:
            diff = delta.seconds
        check_flag = ct.time_check('09:30','15:30')
        #9点30分之前不检查
        if not check_flag:
            diff = 0
        #print(diff)
        if diff > 30 or diff < -10:
            msg = "Error-行情延迟报警,前置地址[%s]行情时间和本地时间间隔为[%s]秒!" % (self.__address, str(diff))
            logger.error(msg)
            ct.send_sms_control('NoLimit', msg)
        else:
            logger.debug("行情延迟监控正常！")


    #查询行情快照
    def test_quiry_market_data(self):       

#        titelname = "TradingDay,SecurityID,ExchangeID,SecurityName,PreClosePrice,OpenPrice,Volume,Turnover,TradingCount,LastPrice,HighestPrice,LowestPrice,BidPrice1,AskPrice1,UpperLimitPrice,LowerLimitPrice,PERatio1,PERatio2,PriceUpDown1,PriceUpDown2,OpenInterest,BidVolume1,AskVolume1,\
#        BidPrice2,BidVolume2,AskPrice2,AskVolume2,BidPrice3,BidVolume3,AskPrice3,AskVolume3,BidPrice4,\
#        BidVolume4,AskPrice4,AskVolume4,BidPrice5,BidVolume5,AskPrice5,AskVolume5,UpdateTime,\
#        UpdateMillisec,ClosePrice,MDSecurityStat,HWFlag"
        titelname = "TradingDay,SecurityID,ExchangeID,SecurityName,PreClosePrice,OpenPrice,Volume,Turnover," \
            "TradingCount,LastPrice,HighestPrice,LowestPrice,BidPrice1,AskPrice1,UpperLimitPrice," \
            "LowerLimitPrice,PERatio1,PERatio2,PriceUpDown1,PriceUpDown2,OpenInterest,BidVolume1,AskVolume1," \
            "BidPrice2,BidVolume2,AskPrice2,AskVolume2,BidPrice3,BidVolume3,AskPrice3,AskVolume3,BidPrice4," \
            "BidVolume4,AskPrice4,AskVolume4,BidPrice5,BidVolume5,AskPrice5,AskVolume5,UpdateTime," \
            "UpdateMillisec,ClosePrice,MDSecurityStat,HWFlag"   
        market_file = "./mylog/pMarketDataField.csv"
        ct.cover_write_file(market_file, titelname)
        quiry_MarketData_field = mdapi.CTORATstpInquiryMarketDataField()
        for list_dict in self.QuriyList:
            if list_dict["ExchangeID"] == 'SSE':
                ExchangeID = mdapi.TORA_TSTP_EXD_SSE
            elif list_dict["ExchangeID"] == 'SZSE':
                ExchangeID = mdapi.TORA_TSTP_EXD_SZSE
            elif list_dict["ExchangeID"] == 'HK':
                ExchangeID = mdapi.TORA_TSTP_EXD_HK
            else:
                ExchangeID = mdapi.TORA_TSTP_EXD_COMM
                           
            quiry_MarketData_field.SecurityID = list_dict["SecurityID"]
            quiry_MarketData_field.ExchangeID = ExchangeID
            #请求编号自增
            self.auto_increase_reqid()
#            time.sleep(1)
            ret=self.__api.ReqInquiryMarketDataMirror(quiry_MarketData_field, self.__req_id)
            if ret!=0:
                logger.warning("Error: [%s] ExchangeID[%s]请求返回错误，ReqInquiryMarketDataMirror ret[%d]" % (list_dict["SecurityID"], quiry_MarketData_field.ExchangeID,ret))
            else:
                logger.info("Ok: [%s] ExchangeID[%s]请求返回正确，ReqInquiryMarketDataMirror ret[%d]" % (list_dict["SecurityID"], quiry_MarketData_field.ExchangeID,ret))
#            time.sleep(1)

    #查询行情快照应答
    def OnRspInquiryMarketDataMirror(self, pMarketDataField, pRspInfo, nRequestID, bIsLast):
        logger.info("OnRspInquiryMarketDataMirror")
        logger.info(pMarketDataField)    
        market_file = "./mylog/pMarketDataField.csv"
        if (pMarketDataField != None):            
            data_list = list(pMarketDataField.values())
            ttl=[]
            for item in data_list:
                if(type(item)==bytes):
                    ttl.append(item.decode('utf-8'))
                else:
                    ttl.append(item)
            #print("ttl:", ttl)
            with open(market_file, 'a+', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(ttl)
        logger.info(pRspInfo)
        logger.info("OnRspInquiryMarketDataMirror: ErrorID[%d] ErrorMsg[%s] RequestID[%d] IsLast[%d]" % (pRspInfo['ErrorID'], pRspInfo['ErrorMsg'], nRequestID, bIsLast))


class mdapi_monitor():
    def __init__(self, CheckData):
#        self.task = check_task
        self.SubscribeList = CheckData['SubscribeMarketData']
        self.QuriyList = CheckData['QuiryMarketData']
        #连接服务器
        self.__address = CheckData['address']           
        logger.info(mdapi.CTORATstpMdApi_GetApiVersion())
        api = mdapi.CTORATstpMdApi_CreateTstpMdApi()
        self.__spi = MdSpi(api, CheckData)
        api.RegisterSpi(self.__spi)
        api.RegisterFront(self.__address)
        api.Init()
        #登陆等待1秒
        time.sleep(1)

    #监控比较marketdata文件
    def monitor_market_data(self):
        #先进行查询操作
        self.__spi.test_quiry_market_data()
        time.sleep(2)
        market_df = pd.read_csv("./mylog/pMarketDataField.csv", dtype=object)
#        print(market_df)
#        print(market_df.columns.size) #列数 
#        print(market_df.iloc[:,0].size)#行数   
        TrD_error_list=[]
        error_list=[]
        if market_df.iloc[:,0].size != 0:
            #判断TradingDay字段是否是当天日期           
            ndates = dt.datetime.now().strftime("%Y%m%d")
            nt_df = market_df[market_df['TradingDay'] != ndates]            
            if len(nt_df) == 0:
                logger.info("[TradingDay]的值%s和当天日期一致" % ndates)
            else:
                #print(nt_df)
                for row in nt_df.itertuples():
                    TrD_error_list.append(str(getattr(row, 'TradingDay')) + "::" + str(getattr(row, 'SecurityID')))
                msg = "Error: 服务器[%s]有证券行情TradingDay字段不是当天日期:[%s]" % (self.__address, ','.join(TrD_error_list))
                logger.error(msg)
                ct.send_sms_control("NoLimit",msg)
            #判断查询的合约行情是否都返回了结果
            
            if len(self.QuriyList) == market_df.iloc[:,0].size :
                logger.info("OK：行情查询返回记录条数和查询列表条数一致")
            else:                
                for dict_item in self.QuriyList:
    #                print("type1",type(dict_item['SecurityID']))
    #                print("type2",type(str(market_df.index[0])))
                    #df_list=list(market_df.index.map(lambda x: str(x)))
                    security_list=list(market_df['SecurityID'])   
                    #valuesDF['OrderTime'] = valuesDF['OrderTime'].map(lambda x: int(x)
    #                print("df_list:", df_list)                   
                    if dict_item['SecurityID'] in security_list:
                        logger.info("SecurityID [%s]查询行情成功" % dict_item['SecurityID'])
                    else:
                        logger.info("SecurityID [%s]查询行情没有返回" % dict_item['SecurityID'])
                        error_list.append(dict_item['SecurityID'])
                msg = "Error: 服务器[%s]mdapi行情查询 没有返回结果的SecurityID列表为：[%s]" % (self.__address, ",".join(error_list))
                logger.error(msg)
                ct.send_sms_control("NoLimit",msg)
        else:
            error_list = self.QuriyList
            msg = "Error:服务器[%s]mdapi行情查询 接口返回为空" % self.__address
            logger.info(msg)
            ct.send_sms_control("NoLimit",msg)
            
        if TrD_error_list == [] and error_list == []:
            msg = "Ok,服务器[%s]mdapi行情查询返回结果正确" % self.__address
            logger.info(msg)
            #ct.send_sms_control("NoLimit",msg)
            return 1
        else:
            return 0
        
    def monitor_subscribe_market_data(self):
        
        start_time = '09:25'
        end_time = '14:59'
        check_flag = ct.time_check(start_time, end_time)
        #nowtime = dt.datetime.now()
        while check_flag:
            #print("登录状态：", self.__spi.login_flag)
            #登录失败
            if not self.__spi.login_flag :
                msg = "行情前置[%s]连接失败" % self.__address
                logger.error(msg)
                ct.send_sms_control("ps_port", msg, '13681919346')
                break
            nowtime = dt.datetime.now()
            print(nowtime,"call monitor_subscribe_market_data")
            time.sleep(5)
            check_flag = ct.time_check(start_time, end_time)
        #return 1

class MyThread(threading.Thread):

    def __init__(self,func,args,name=''):
        threading.Thread.__init__(self)
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


def main(argv):
    
    try:
        yaml_path = './config/api_monitor_logger.yaml'
        ct.setup_logging(yaml_path)
        
        with open('./config/api_monitor_config.json', 'r') as f:
            JsonData = json.load(f)   
            
        manual_task = ''
        try:
            opts, args = getopt.getopt(argv,"ht:",["task="])
        except getopt.GetoptError:
            print('mdapi_check.py -t <task> or you can use -h for help')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print('python trade_monitor.py -t <task>\n \
                    parameter -t comment: \n \
                    use -t can input the manul single task.\n \
                    task=["qry_market_data","mem","fpga","db_init","db_trade","errorLog"].  \n \
                    task="qry_market_data" means porcess and port monitor  \n \
                    task="qry_security" means memory monitor  \n \
                    task="db_trade" means db trading data monitor  \n \
                    task="errorLog" means file error log monitor  \n \
                    task="self_monitor" means self check monitor  \n \
                    task="smss" means check the sms send status  \n \
                    task="sms0" means set sms total_count=0  \n \
                    fpga_monitor and db_init_monitor just execute once on beginning ' )            
                sys.exit()
            elif opt in ("-t", "--task"):
                manual_task = arg
                
        if manual_task not in ["qry_market_data","qry_security","fpga","db_init","db_trade","errorLog","self_monitor","smss","sms0","sms100"]:
            logger.warning("[task] input is wrong, please try again!")
            sys.exit()
            
        else:
            logger.info('manual_task is:%s' % manual_task)
            logger.info("Start to excute the mdapi monitor")          
            for PyMdApi_CheckData in JsonData['PyMdApi']:            
                if manual_task == 'qry_market_data':
                    logger.info("Start to excute the qry_market_data monitor")        
                    md_test = mdapi_monitor(PyMdApi_CheckData)
                    md_test.monitor_market_data()
    #                str = input("\n")
                else:
                    print("Input python mdapi_test.py -h for help")
        
    except Exception:
        logger.error('Faild to run mdapi monitor!', exc_info=True)
    finally:
        for handler in logger.handlers:
            logger.removeHandler(handler)


#通过mdapi订阅行情查询检查
def mdapi_subs_monitor_task():
    yaml_path = './config/api_monitor_logger.yaml'
    ct.setup_logging(yaml_path)
    with open('./config/api_monitor_config.json', 'r') as f:
        JsonData = json.load(f)
    
    try:
        res_flag = 0
#         for PyMdApi_CheckData in JsonData['PyMdApi']:
# #        PyMdApi_CheckData = JsonData['PyMdApi']
#             md_test = mdapi_monitor(PyMdApi_CheckData)
#             res = md_test.monitor_subscribe_market_data()
#         #     res_flag += res
        # if res_flag == len(JsonData['PyMdApi']):
        #     msg = "Ok,所有服务器mdapi行情订阅检查返回结果正确！"
        #     logger.info(msg)
        #     ct.send_sms_control("NoLimit", msg)
        # else:
        #     logger.info("Error: 有服务器mdapi行情订阅检查返回结果不正确！")
        thrlist = range(len(JsonData['PyMdApi']))
        threads=[]
        for (i,PyMdApi_CheckData) in zip(thrlist, JsonData['PyMdApi']):
            md_test = mdapi_monitor(PyMdApi_CheckData)
            t = MyThread(md_test.monitor_subscribe_market_data,(),md_test.monitor_subscribe_market_data.__name__ + str(i))
            threads.append(t)
            
        for i in thrlist:
            threads[i].start()
        for i in thrlist:       
            threads[i].join()
    except Exception as e:
        msg = str(e)
        logger.error("mdapi subscribe monitor 异常：" + msg)


if __name__ == "__main__":
    #main(sys.argv[1:])
    mdapi_subs_monitor_task()
