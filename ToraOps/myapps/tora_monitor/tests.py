from django.test import TestCase
from django.conf import settings
import django
import os
import sys
import json

sys.path.extend(['D:\\my_project\\python3\\django_project\\ToraOps_project\\ToraOps'])
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ToraOps.settings')
django.setup()
sys.path.append('..')
from myapps.toraapp import models
from django.core.mail import send_mail

# Create your tests here.


def get_machine():
    machine = models.ShelfMachine.objects.filter(is_active='1').first()
    print(machine, type(machine))
    print(machine.inner_ip)

def test_job():
    print("我是apscheduler任务")

def test_job2(para='job2'):
    print("我是apscheduler任务" + para)

def get_choices():
    config_path = os.path.join(settings.BASE_DIR, "config")
    choices_file = os.path.join(config_path,'form_choices.json')
    with open(choices_file, 'r', encoding='UTF-8') as f:
        Jsondata = json.load(f)
        print(type(Jsondata), Jsondata) 
    return Jsondata


#ttc = map(lambda tc: (tc.key, tc[key]), tc)
def dict2tuple(dictData):
    temp_list = []
    for key in dictData:
        temp_list.append((key,dictData[key]))
    print(temp_list)
    return tuple(temp_list)
    # print(ttc)
    # print(TRIGGER_CHOICES==ttc)

# choices = get_choices()
# TRIGGER_CHOICES = (
#     (u'date', u'一次性'),
#     (u'interval', u'固定间隔'),
#     (u'cron', u'crontab格式'),
# )
# STATUS_CHOICES = (
#     (u'0', u'未激活'),
# )
# print(type(choices))
# print(choices['tora_monitor'])
# tcc = dict2tuple(choices['tora_monitor']['TRIGGER_CHOICES'])
# print(tcc)
msg = "上架完成测试"
send_res = send_mail(msg, msg, 'zhangwei@n-sight.com.cn',
            ['158279489@qq.com','zhangwei@n-sight.com.cn'], fail_silently=False)