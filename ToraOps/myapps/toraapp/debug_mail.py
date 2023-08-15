
#site= {'name': '我的博客地址', 'alexa': 10000, 'url':'http://blog.csdn.net/uuihoo/'}
#pop_obj=site.pop('name') # 删除要删除的键值对，如{'name':'我的博客地址'}这个键值对
# for key in ['name','alexa']:
#     del site[key]
# print(site)

# new_dic = site.pop('name')
# print(site)

from django.core.mail import send_mail
from django.conf import settings
import django
import os
import sys
sys.path.extend(['/home/trade/tora_ops/ToraOps'])
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ToraOps.settings')
django.setup()


business = ['hxzq', 'sp', 'rzrq', 'qh']
tele_pattern = ['tcp', 'udp']
trade_app_type = ['tradeserver1', 'fens1', 'fens2', 'fens3']
mq_type = ['md_L1', 'sse_md_L2', 'szse_md_L2A','szse_md_L2B','md_L2', 'qh_L1']

#节点业务：
hxzq_tradeserver1 = '10.188.80.8:6500'
sp_tradeserver1 = '10.188.80.26:15500'
rzrz_tradeserver1 = '10.188.80.64:14500'
hxzq_fens1 = 'tcp://10.188.80.18:42370'
hxzq_fens2 = 'tcp://10.188.80.28:52370'

#节点-业务：
# md_L1_tcp
# md_L1_udp
# md_L2_tcp
# md_L2_udp
# sse_md_L2_tcp
# sse_md_L2_udp
# szse_md_L2A_tcp
# szse_md_L2B_udp
qh_L1_tcp = "10.188.80.18: 8787"



hq_addr = "10.188.80.18: 8787"
content1 = """
        【股票】
        沪&深股票L2 组播行情前置地址：udp://224.224.224.232:5889
        (使用10.188.82.X地址段（具体以邮件为准）收取、SourceIP：10.188.82.7或NULL(推荐方式))
        #RegisterMulticast("udp://224.224.224.232:5889","10.188.82.X”,NULL)
        
        L1沪&深股票行情(MD)交易(TD) FENS的双路地址: tcp://10.188.80.18:42370,tcp://10.188.80.28:52370
        #注册单个fens地址，如：RegisterNameServer("tcp://10.188.80.18:42370")
        #注册多个fens地址用逗号连接，如：RegisterNameServer("tcp://10.188.80.18:42370,tcp://10.188.80.28:52370")（推荐方式）
        
        【期权】
        L1沪&深期权行情(MD)：10.188.80.26 : 15402
        交易(TD)：10.188.80.26 : 15500
        
        【两融】
        L1沪&深股票行情(MD)：10.188.80.64 : 14402
        交易(TD)：10.188.80.64 : 14500
        
        【期货】
        L1期货行情(MD)：%s
        """ % (hq_addr)


print(content1)

send_mail('上架完成', content, 'zhangwei@n-sight.com.cn',
        ['158279489@qq.com'], fail_silently=False)

#mail_dict = {"hxzq":{}, "sp":{}, "rzrq":{}, "qh":{}}
#for item_busi in business

