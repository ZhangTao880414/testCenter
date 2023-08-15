#import monitor_task as mtask

#mtask.test_job()

# nodeConfig = {'hxzq': {'trade': {'tradeserver1': {'ip_addr': '10.224.123.144', 'port': '8500', 'intnet_addr': None, 'intnet_port': None}, 'tradeserver2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'node_md_L1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}}, 'mq': {'md_L2': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'md_L1': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'sse_md_L2': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'szse_md_L2A': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'szse_md_L2B': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'qh_L1': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}}}, 'sp': {'trade': {'tradeserver1': {'ip_addr': '10.224.123.144', 'port': '8500', 'intnet_addr': None, 'intnet_port': None}, 'tradeserver2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'node_md_L1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}}, 'mq': {'md_L2': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'md_L1': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'sse_md_L2': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'szse_md_L2A': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'szse_md_L2B': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'qh_L1': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}}}, 'rzrq': {'trade': {'tradeserver1': {'ip_addr': '10.224.123.144', 'port': '8500', 'intnet_addr': None, 'intnet_port': None}, 'tradeserver2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'node_md_L1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}}, 'mq': {'md_L2': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'md_L1': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'sse_md_L2': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'szse_md_L2A': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'szse_md_L2B': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'qh_L1': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}}}, 'qh': {'trade': {'tradeserver1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'tradeserver2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'node_md_L1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'trade_front3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'mq_front3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens1': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens2': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}, 'fens3': {'ip_addr': '', 'port': '', 'intnet_addr': '', 'intnet_port': ''}}, 'mq': {'md_L2': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'md_L1': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'sse_md_L2': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'szse_md_L2A': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'szse_md_L2B': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}, 'qh_L1': {('tcp', 'tcp连接'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}, ('udp', 'upd组播'): {'ip_addr': '', 'port': '', 'md_rec_addr': '', 'source_ip': ''}}}}}
# for item_bussi in ['hxzq','sp','rzrq']:
#     print(nodeConfig[item_bussi]['mq']['md_L2']['udp'])
from functools import wraps

job_args = 'job1'

def job1():
    print("I am job1!")

def call_func(func):
    func()

#eval(job_args)()

#call_func(eval(job_args))


 
def a_new_decorator(a_func):
    @wraps(a_func)
    def wrapTheFunction(*args, **kwargs):
        print("I am doing some boring work before executing a_func()")
        res = a_func(*args, **kwargs)
        if res:
            print("I am doing some boring work after executing a_func()")
        else:
            print("false....")
    return wrapTheFunction
 
@a_new_decorator
def job1(i=1,b=3):
    print("I am job1!")
    print("b:",b)
    if i==1:
        return 1
    return 0

#job1(1,6)
def test23(b):
    try:
        a = 3/b
    except Exception as e:
        print(str(e))
        return -1
    return a

res = {'data':''}
msg = [{'server_info': '192.168.10.121@@dgnf@@F03@@U13@@DL380 Gen10@@FS1920012@@2', 'data': {'loss': '100%', 'rtt': 9999}}]

res['data'] = str(msg)
print(res)