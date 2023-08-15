from django.dispatch import receiver
from django.db.models import signals
from myapps.toraapp.tools.signals import task_update
#from myapps.toraapp.models import ShelfMachine, ToraCustomer, NodeInfo, SystemUserInfo, ROOM_CHOICES
from myapps.toraapp import models as tmodels
from myapps.tora_monitor import models as mmodels
from myapps.tora_monitor import views as mviews
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.forms.models import model_to_dict
import copy
import pandas as pd
import datetime as dt
import common.common_tools as ct
import common.tora_django_common as tdc
import common.res_pool_manager as poolm
from apscheduler.schedulers.background import BackgroundScheduler
import logging
logger = logging.getLogger('django')



# @receiver(post_update)
# def post_update_callback(sender, **kwargs):
#     print(kwargs["sys_user_passwd"])
#     print("post_update_success")

oper_mails = ['zhangxin@n-sight.com.cn','zhangzhongtian@n-sight.com.cn','daiwei@n-sight.com.cn',
            'dukeqin@n-sight.com.cn','zhangwei@n-sight.com.cn','yuqihang@n-sight.com.cn']

@ct.async_run
def send_shelf_apply_mail(taskflow_obj):
    #vpnInfo = tdc.get_vpnInfo(taskflow_data['engine_room'])
    #vpn_passwd = 'hxzq123'
    taskflow_data = model_to_dict(taskflow_obj)
    print("taskflow_data:", taskflow_data)
    engineRoomStr = dict(tmodels.ROOM_CHOICES)[taskflow_data['engine_room']]
    ownershipStr = dict(tmodels.OWNER_CHOICES)[taskflow_data['']]
    purposeStr = dict(tmodels.PURPOSE_CHOICES)[taskflow_data['purpose']]
    assert_typeStr = dict(tmodels.ASSERT_CHOICES)[taskflow_data['assert_type']]
    is_new_vpnStr = dict(tmodels.BOOLEAN_CHOICES)[taskflow_data['is_new_vpn']]

    nodeobj = tmodels.NodeInfo.objects.get(pk=taskflow_data['node'])
    node_no = nodeobj.__getattribute__('node_no')
    mail_title = '【机房:{0}】【节点:{1}】【{2}】上架申请'.format(engineRoomStr, node_no, taskflow_data['custgroup_name'])
    content = """
        您好，有服务器上架申请任务，服务器信息如下：

        客户：{0}
        机房：{1}
        节点编号：{2}
        物主身份：{3}
        使用方式：{4}
        是否新分配vpn：{5}
        vpn用户名：{6}
        授权外网地址端口：{7}
        资产类型：{8}
        服务器品牌：{9}
        服务器型号：{10}
        服务器序列号：{11}
        操作系统：{12}
        系统版本：{13}
        备注：{14}
        客户其他信息：{15}

        """ .format(taskflow_data['custgroup_name'], engineRoomStr, node_no, ownershipStr, purposeStr,
                is_new_vpnStr, taskflow_data['vpn_user_name'], taskflow_data['access_address'], 
                assert_typeStr, taskflow_data['server_brand'], taskflow_data['server_model'],
                taskflow_data['serial_number'], taskflow_data['os'], taskflow_data['os_version'],
                taskflow_data['comment'], taskflow_data['other_msg'])

    #去掉前面空格
    content_format = content.replace('    ','')
    print(content_format)

    res = send_mail(mail_title, content_format, 'zhangwei@n-sight.com.cn',
                    oper_mails, fail_silently=False)

    logger.info("发送邮件%s结果：%s" % (mail_title, str(res)))
    return res



@ct.async_run
def send_shelf_mail(taskflow_data):
    vpnInfo = tdc.get_vpnInfo(taskflow_data['engine_room'])
    #vpn_passwd = 'hxzq123'
    print("taskflow_data:", taskflow_data)
    engineRoomStr = dict(tmodels.ROOM_CHOICES)[taskflow_data['engine_room']]
    nodeobj = tmodels.NodeInfo.objects.get(pk=taskflow_data['node'])
    node_no = nodeobj.__getattribute__('node_no')
    mail_title = '【机房:{0}】【节点:{1}】【{2}】上架完成'.format(engineRoomStr, node_no, taskflow_data['custgroup_name'])
    content = """
        您好，服务器上架已完成，系统信息如下：

        服务器内网地址：{0}
        系统用户：{1}
        系统初始密码：{2}
        vpn地址：{3}
        vnp账号：{4}
        vpn初始密码：{5}

        """ .format(taskflow_data['inner_ip'], taskflow_data['sys_user_name'], taskflow_data['sys_user_passwd'], vpnInfo['vpn_address'], taskflow_data['vpn_user_name'], vpnInfo['vpn_passwd'])

    node_mail_content = tdc.get_node_mail_content(taskflow_data['node'])
    print("node_mail_content:", node_mail_content)
    content += node_mail_content
    #去掉前面空格
    content_format = content.replace('    ','')
    print(content_format)

    res = send_mail(mail_title, content_format, 'zhangwei@n-sight.com.cn',
                    oper_mails, fail_silently=False)

    logger.info("发送邮件%s结果：%s" % (mail_title, str(res)))
    return res


@ct.async_run
def send_offShelf_mail(taskflow_data):
    print("taskflow_data:", taskflow_data)
    engineRoomStr = dict(tmodels.ROOM_CHOICES)[taskflow_data['engine_room']]
    nodeobj = tmodels.NodeInfo.objects.get(pk=taskflow_data['node'])
    node_no = nodeobj.__getattribute__('node_no')
    mail_title = '【机房:{0}】【节点:{1}】【{2}】【服务器：{3}】下架完成'.format(engineRoomStr, node_no, taskflow_data['custgroup_name'], taskflow_data['inner_ip'])
    content = """
        您好，服务器下架已完成，系统信息如下：
        服务器内网地址：{0}
        品牌：{1}
        型号：{2}
        SN: {3}
        """.format(taskflow_data['inner_ip'], taskflow_data['server_brand'],taskflow_data['server_model'],taskflow_data['serial_number'])
    #去掉前面空格
    content_format = content.replace('    ', '')  
    print(content_format)

    res = send_mail(mail_title, content_format, 'zhangwei@n-sight.com.cn',
                    oper_mails, fail_silently=False)

    logger.info("发送邮件%s结果：%s" % (mail_title, str(res)))
    return res





@ct.async_run
def send_share_apply_mail(taskflow_data):
    print("taskflow_data:", taskflow_data)
    vpnInfo = tdc.get_vpnInfo(taskflow_data['engine_room'])
    engineRoomStr = dict(tmodels.ROOM_CHOICES)[taskflow_data['engine_room']]
    nodeobj = tmodels.NodeInfo.objects.get(pk=taskflow_data['node'])
    node_no = nodeobj.__getattribute__('node_no')
    mail_title = '【机房:{0}】【节点:{1}】【{2}】【服务器：{3}】共享资源分配完成'.format(engineRoomStr, node_no, taskflow_data['custgroup_name'], taskflow_data['inner_ip'])
    content = """
        您好，共享服务器资源已分配，系统信息如下：
        服务器内网地址：{0}
        系统用户：{1}
        系统初始密码：{2}
        vpn地址：{3}
        vnp账号：{4}
        vpn初始密码：{5}

        """ .format(taskflow_data['inner_ip'], taskflow_data['sys_user_name'], taskflow_data['sys_user_passwd'], vpnInfo['vpn_address'], taskflow_data['vpn_user_name'], vpnInfo['vpn_passwd'])
   
    node_mail_content = tdc.get_node_mail_content(taskflow_data['node'])
    content += node_mail_content
    #去掉前面空格
    content_format = content.replace('    ', '')  
    print(content_format)

    res = send_mail(mail_title, content_format, 'zhangwei@n-sight.com.cn',
                    oper_mails, fail_silently=False)

    logger.info("发送邮件%s结果：%s" % (mail_title, str(res)))
    return res


@ct.async_run
def send_share_release_mail(taskflow_data):
    print("taskflow_data:", taskflow_data)
    engineRoomStr = dict(tmodels.ROOM_CHOICES)[taskflow_data['engine_room']]
    nodeobj = tmodels.NodeInfo.objects.get(pk=taskflow_data['node'])
    node_no = nodeobj.__getattribute__('node_no')
    mail_title = '【机房:{0}】【节点:{1}】【{2}】【服务器：{3}】共享资源回收完成'.format(engineRoomStr, node_no, taskflow_data['custgroup_name'], taskflow_data['inner_ip'])
    content = """
        您好，共享服务器资源已回收，系统信息如下：
        服务器内网地址：{0}
        系统账号：{1}
        vpn账号：{2}
        """.format(taskflow_data['inner_ip'], taskflow_data['sys_user_name'],taskflow_data['vpn_user_name'])
    #去掉前面空格
    content_format = content.replace('    ', '')  
    print(content_format)

    res = send_mail(mail_title, content_format, 'zhangwei@n-sight.com.cn',
                    oper_mails, fail_silently=False)

    logger.info("发送邮件%s结果：%s" % (mail_title, str(res)))
    return res


# def add_stuff(bar):
#     item = Item.objects.create(foo=bar)
#     return item

@receiver(task_update)
def task_update_callback(sender, **kwargs):
    try:
        request = kwargs["request"]
        new_req = request.data
        new_req['operator'] = request.user
        new_req["is_active"] = '1'
        #cur_user_obj = User.objects.get(username=)
        logger.info(new_req)
        mail_data={}
        mail_data = copy.deepcopy(new_req)
        #print("task_update_success")
        #cust_obj = ToraCustomer.objects.get(custgroup_name=new_req['custgroup_name'])
        print("id:", new_req['customer'], type(new_req['customer']))
        cust_obj = tmodels.ToraCustomer.objects.get(id=new_req['customer'])
        #增加上架信息
        if new_req["task_type"] == "1" :
            if new_req["ownership"] == '1':
                new_req["owner"] = cust_obj
            else:
                #华鑫资产增加一条ID=1的记录
                hx = tmodels.ToraCustomer.objects.get_or_create(custgroup_name='华鑫', \
                    defaults={'phone':'13681919346','email':'zhangwei@n-sight.com.cn','operator':'1'})
                new_req["owner"] = hx
            #del new_req["customer"]
            user_name = new_req['sys_user_name']
            user_passwd = new_req['sys_user_passwd']
            for key in ['custgroup_name','task_status','task_type', 'ownership', 'is_new_vpn', 
                    'vpn_user_name', 'sys_user_name', 'sys_user_passwd', 'access_action', 
                    'access_address', 'access_finished', 'other_msg', 'customer']:
                del new_req[key]
            #print(new_req)
            # create_req = {}
            # create_req = new_req
            sn = new_req.pop('serial_number')
            #print("sn:", sn)
            # del create_req["serial_number"]
            # print("new_req['serial_number']:",create_req)
            node_id = new_req["node"]
            node_obj = tmodels.NodeInfo.objects.get(pk=int(node_id))
            #print("node_obj:", node_obj)
            new_req["node"] = node_obj
            #print(type(new_req["owner"]), new_req["owner"])
            #上架日期
            new_req['shelf_date'] = dt.datetime.now().strftime("%Y-%m-%d")
            tuple_vlue = tmodels.ShelfMachine.objects.get_or_create(serial_number=sn, defaults=new_req)
            #print(tuple_vlue[0],type(tuple_vlue[0]), tuple_vlue[1])
            shelf_machine = tuple_vlue[0]
            is_created = tuple_vlue[1]
            #print(shelf_machine,type(shelf_machine))
            #print(type(cust_obj),cust_obj,cust_obj.id)
            #增加toraapp_shelfmachine_customer表
            shelf_machine.customer.add(cust_obj.id)
            # # 先删除所有在绑定
            # shelf_machine.customer.set([cust_obj])
            #增加SystemUserInfo表
            sys_user_tuple = tmodels.SystemUserInfo.objects.get_or_create(inner_ip=new_req['inner_ip'],sys_user_name=user_name, \
                                defaults={'engine_room': new_req['engine_room'],'sys_user_passwd': user_passwd, 'cur_status': '1', 'customer': cust_obj, 'operator': new_req['operator']})
            #print("sys_user_tuple:", sys_user_tuple)
            #发送上架成功邮件
            try:
                res = send_shelf_mail(mail_data)
            except Exception:
                res = 0
                err_msg = 'Faild to send mail!'
                logger.error(err_msg, exc_info=True)
                ct.send_sms_control('NoLimit', err_msg, '13681919346')
        #删除下架机器
        elif new_req["task_type"] == "2" :
            machine_obj = tmodels.ShelfMachine.objects.get(serial_number=new_req['serial_number'])
            machineIP={'inner_ip': machine_obj.inner_ip,
                        'outer_ip': machine_obj.outer_ip,
                        'high_trade_ip': machine_obj.high_trade_ip,
                        'high_mqA_ip': machine_obj.high_mqA_ip,
                        'high_mqB_ip': machine_obj.high_mqB_ip,
                        'other_ip': machine_obj.other_ip,
                        'ipmi_ip': machine_obj.ipmi_ip}
            machine_obj.customer.clear()
            machine_obj.delete()
            #IP回收，U位回收
            tdc.realeaseCustIP(machineIP)
            #发送下架成功邮件
            try:
                res = send_offShelf_mail(mail_data)
            except Exception:
                res = 0
                err_msg = 'Faild to send mail!'
                logger.error(err_msg, exc_info=True)
                ct.send_sms_control('NoLimit', err_msg, '13681919346')

        elif new_req["task_type"] == "6" :
            #置系统用户状态为待回收
            #置vpn用户状态为待回收
            #发送回收成功邮件
            try:
                res = send_offShelf_mail(mail_data)
            except Exception:
                res = 0
                err_msg = 'Faild to send mail!'
                logger.error(err_msg, exc_info=True)
                ct.send_sms_control('NoLimit', err_msg, '13681919346')
    
    except Exception:
        err_msg = 'Faild to run task_update_callback!'
        logger.error(err_msg, exc_info=True)
        ct.send_sms_control('NoLimit', err_msg, '13681919346')




# @receiver(signals.post_init, sender=mmodels.MonitorJob)
# def modify_monitorJob_post_init(sender, instance, **kwargs):
#     print("instance.is_active111:", instance.is_active)
#     instance.__original_name = instance.is_active
 
# @receiver(signals.post_save, sender=mmodels.MonitorJob)
# def modify_monitorJob(sender, instance, created, **kwargs):
#     print("instance.is_active2:", instance.is_active)
#     if created:
#         if instance.is_active == '1':
#             print("新增监控项")
#             print("instance:", type(instance), instance)
#             mviews.process_monitorJob('add', instance)
#     elif not created and instance.__original_name != instance.is_active: 
#         #print("job:",scheduler.get_jobs()) 
#         if instance.is_active == '1':
#             print("do监控项激活")
#             #print(mviews.scheduler.get_jobs())
#             print("instance:", type(instance), instance)
#             print("instance:", type(instance), instance.job_args)
#             mviews.process_monitorJob('resume', instance)
#         else:
#             print("do监控项停止")
#             #print(mviews.scheduler.get_jobs())
#             #mviews.print_job()
#             print("instance:", type(instance), instance.job_args)
#             mviews.process_monitorJob('pause', instance)


# @receiver(signals.post_delete, sender=mmodels.MonitorJob)
# def delete_monitorJob(sender, instance, **kwargs):
#     print("instance: ", instance)
#     print("删除监控项")
#     mviews.process_monitorJob('remove', instance)


# @receiver(monitor_job_update)
# def monitor_job_update_callback(sender, **kwargs):
#     try:
#         print("更新监控任务")
#     except Exception:
#         err_msg = 'Faild to run monitor_job_update_callback!'
#         logger.error(err_msg, exc_info=True)
#         ct.send_sms_control('NoLimit', err_msg, '13681919346')


#增加修改taskflow时操作
@receiver(signals.post_init, sender=tmodels.TaskFlow)
def modify_taskFlow_post_init(sender, instance, **kwargs):
    print("taskFlow's task_type:", instance.task_type)
    print("taskFlow's status:", instance.task_status)
    instance.__original_name = instance.task_status
    instance.__original_other_msg = instance.other_msg
    print("post_init task_status:", instance.__original_name)


@receiver(signals.post_save, sender=tmodels.TaskFlow)
def modify_taskFlow(sender, instance, created, **kwargs):
    print(type(kwargs))
    print("instance.task_status2:", instance.task_status)
    #print(**kwargs)
    # print("kwargs:", kwargs['signal']["request"])
    # request = kwargs["request"]
    #print(type(instance))
    new_req = model_to_dict(instance)
    #print(new_req)
    #return 1
    #new_req['operator'] = 'zhangwei'
    logger.info(new_req)
    mail_data={}
    mail_data = copy.deepcopy(new_req)

    # msg = "上架完成测试"
    # send_res = send_mail(msg, msg, 'zhangwei@n-sight.com.cn',
    #             ['158279489@qq.com','zhangwei@n-sight.com.cn'], fail_silently=False)
    # print(send_res)
    # return 1
    if created:
        print("增加新的taskFlow！")
        if instance.task_type == '1':
            logger.info("新增加上架任务")
            print("other_msg:",instance.other_msg)
            #发送上架申请邮件
            send_shelf_apply_mail(instance)
        elif instance.task_type == '2':
            logger.info('新增设备下架')
        elif instance.task_type == '3':
            logger.info('新增更改操作系统')
        elif instance.task_type == '4':
            logger.info('新增服务器维修')
        elif instance.task_type == '5':
            logger.info('新增服务器移位')
        elif instance.task_type in ['6','7','8','9']:
            #logger.info('新增共享资源申请')
            print("instance:", instance)
            print("id, access_action", instance.id, instance.access_action)
            # if instance.access_action != '0' :
            #     tdc.auto_add_access_apply(instance.id)
            res_manager = poolm.res_pool_manager(instance.id)
            res_manager.process_resource_apply()
        # elif instance.task_type == '7':
        #     logger.info('新增共享资源回收')
        # elif instance.task_type == '8':
        #     logger.info('外网授权网络申请')
        # elif instance.task_type == '9':
        #     logger.info('操作员强制回收资源')
        else:
            logger.info("新增其他任务")
      
    #elif not created and instance.__original_name != instance.task_status and instance.task_status == '1': 
    elif not created:
        #状态修改为完成
        print(instance.id,instance.__original_name,instance.task_status)
        if instance.__original_name != instance.task_status and instance.task_status == '1': 
            print("taskFlow's task_type2:", instance.task_type)
            print("taskFlow's status2:", instance.task_status)
            is_new_vpn_list = instance.is_new_vpn.split(';')
            vpn_name_list = instance.vpn_user_name.split(';')
            vpn_phone_list = instance.vpn_phone.split(';')
            vpn_df = pd.DataFrame({'is_new_vpn':is_new_vpn_list, 'vpn_name': vpn_name_list, 'vpn_phone': vpn_phone_list})
            vpn_num = len(vpn_name_list)
            #exist_user = tdc.query_vpn_user(instance.engine_room, instance.vpn_user_name)
            #上架完成
            if instance.task_type == '1' :
                new_req["is_active"] = '1'
                # mail_data={}
                # mail_data = copy.deepcopy(new_req)
                #print("task_update_success")
                #cust_obj = ToraCustomer.objects.get(custgroup_name=new_req['custgroup_name'])
                print("id:", new_req['customer'], type(new_req['customer']))
                cust_obj = tmodels.ToraCustomer.objects.get(id=new_req['customer'])
                print("cust_obj:", type(cust_obj),cust_obj)
                print("operator:", new_req['operator'], type(new_req['operator']))
                oper_obj = tmodels.User.objects.get(id=new_req['operator'])
                new_req['operator'] = oper_obj
                logger.info("服务器%s,[%s]上架完成！" % (instance.serial_number, instance.inner_ip))
                if new_req["ownership"] == '1':
                    new_req["owner"] = cust_obj
                else:
                    #华鑫资产增加一条ID=1的记录
                    hx, is_created_hx = tmodels.ToraCustomer.objects.get_or_create(custgroup_name='华鑫', \
                        defaults={'phone':'13681919346','email':'zhangwei@n-sight.com.cn','operator':'1'})
                    new_req["owner"] = hx
                #del new_req["customer"]
                print("owner:", new_req["owner"])
                user_name = new_req['sys_user_name']
                user_passwd = new_req['sys_user_passwd']
                for key in ['apply_source','custgroup_name','email','task_status','task_type', 'ownership', 'is_new_vpn', 
                        'vpn_user_name', 'vpn_phone', 'sys_user_name', 'sys_user_passwd', 'access_action', 
                        'access_address', 'access_finished', 'other_msg', 'customer', 'modify_oper']:
                    del new_req[key]
                #print(new_req)
                # create_req = {}
                # create_req = new_req
                sn = new_req.pop('serial_number')
                #print("sn:", sn)
                # del create_req["serial_number"]
                # print("new_req['serial_number']:",create_req)
                node_id = new_req["node"]
                node_obj = tmodels.NodeInfo.objects.get(pk=int(node_id))
                #print("node_obj:", node_obj)
                new_req["node"] = node_obj
                print(type(new_req["owner"]), new_req["owner"])
                tuple_vlue = tmodels.ShelfMachine.objects.get_or_create(serial_number=sn, defaults=new_req)
                print(tuple_vlue[0],type(tuple_vlue[0]), tuple_vlue[1])
                shelf_machine = tuple_vlue[0]
                is_created = tuple_vlue[1]
                print(shelf_machine,type(shelf_machine))
                #print(type(cust_obj),cust_obj,cust_obj.id)
                #增加toraapp_shelfmachine_customer表
                shelf_machine.customer.add(cust_obj.id)
                # # 先删除所有在绑定
                # shelf_machine.customer.set([cust_obj])
                #增加SystemUserInfo表
                sys_user_tuple = tmodels.SystemUserInfo.objects.get_or_create(inner_ip=new_req['inner_ip'],sys_user_name=user_name, \
                                    defaults={'engine_room': new_req['engine_room'],'sys_user_passwd': user_passwd, 'cur_status': '1', 'customer': cust_obj, 'operator': new_req['operator']})
                #print("sys_user_tuple:", sys_user_tuple)
                
                #当客户独用或者共用时自动创建vpn
                if instance.purpose in ['1','2']:
                    for row in vpn_df.itertuples():
                        #print(getattr(row, 'c1'), getattr(row, 'c2'))
                    #if (exist_user == 0 and instance.is_new_vpn == '1') or (exist_user == 1 and instance.is_new_vpn == '0'):
  
                        #自动创建vpn和建立资源对应关系
                        process_vpn_res = tdc.add_vpnuser_resource(instance.engine_room, instance.custgroup_name, getattr(row, 'vpn_name'), getattr(row, 'vpn_phone'), instance.inner_ip, instance.os)
                    # else:
                    #     msg = "vpn账号：%s is_new_vpn字段: %s 不正确,不自动创建vpn" % (instance.vpn_user_name,instance.is_new_vpn)
                    #     logger.error(msg)
                    #     ct.send_sms_control('NoLimit', msg, '13681919346')
                    #     tdc.set_taskflow_fail(instance.id, msg)
                    #     process_vpn_res = 0  
                #奇点自用不需要创建vpn
                else:
                    logger.info("奇点自用不需要创建vpn")
                    process_vpn_res = 1
                
                if process_vpn_res:
                    logger.info("自动处理vpnuser成功，将发送上架成功邮件")
                    #发送上架成功邮件
                    send_shelf_mail(mail_data)
                else:
                    err_msg = "vpn用户创建失败,不发邮件"
                    logger.error(err_msg)
            #删除下架机器
            elif instance.task_type == "2" :
                machine_obj = tmodels.ShelfMachine.objects.get(serial_number=new_req['serial_number'])
                machineIP={'inner_ip': machine_obj.inner_ip,
                            'outer_ip': machine_obj.outer_ip,
                            'high_trade_ip': machine_obj.high_trade_ip,
                            'high_mqA_ip': machine_obj.high_mqA_ip,
                            'high_mqB_ip': machine_obj.high_mqB_ip,
                            'other_ip': machine_obj.other_ip,
                            'ipmi_ip': machine_obj.ipmi_ip}
                machine_obj.customer.clear()
                machine_obj.delete()
                #IP回收，U位回收
                tdc.realeaseCustIP(machineIP)
                #发送下架成功邮件
                send_offShelf_mail(mail_data)
                #if exist_user == 1:
                # if instance.ownership == '1' :
                    # logger.info("客户机器下架成功，清除vpn资源对应关系")
                for row in vpn_df.itertuples():
                    tdc.release_vpnuser_resource(instance.engine_room, instance.custgroup_name, getattr(row, 'vpn_name'), getattr(row, 'vpn_phone'), instance.inner_ip)
                # else:
                #     logger.info("其他下架机器，不做清除vpn资源操作")
                # else:
                #     msg = "vpn账号：%s 不存在,不做清除vpn资源操作" % instance.vpn_user_name
                #     logger.error(msg)
                #     ct.send_sms_control('NoLimit', msg, '13681919346')
            #共用资源申请
            elif instance.task_type == "6" :
                #分配共用服务器用户
                #创建vpn用户
                #if (exist_user == 0 and instance.is_new_vpn == '1') or (exist_user == 1 and instance.is_new_vpn == '0'):
                #if instance.is_new_vpn == '1' and instance.vpn_user_name != None :
                for row in vpn_df.itertuples():
                    #自动创建vpn
                    process_vpn_res = tdc.add_vpnuser_resource(instance.engine_room, instance.custgroup_name, getattr(row, 'vpn_name'), getattr(row, 'vpn_phone'), instance.inner_ip, instance.os)
                # else:
                #     msg = "vpn账号：%s is_new_vpn字段: %s 不正确,不自动创建vpn" % (instance.vpn_user_name,instance.is_new_vpn)
                #     logger.error(msg)
                #     ct.send_sms_control('NoLimit', msg, '13681919346')
                #     tdc.set_taskflow_fail(instance.id, msg)
                #发送分配成功邮件
                if process_vpn_res:
                    logger.info("新建vpnuser成功，将发送邮件")
                    res = send_share_apply_mail(mail_data)
                else:
                    err_msg = "vpn用户创建失败,不发邮件"
                    logger.error(err_msg)
            #共用资源回收
            elif instance.task_type == "7" :
                #置系统用户状态为待回收
                # if exist_user == 1:
                logger.info("共享资源回收，清除vpn资源对应关系")
                for row in vpn_df.itertuples():
                    tdc.release_vpnuser_resource(instance.engine_room, instance.custgroup_name, getattr(row, 'vpn_name'), getattr(row, 'vpn_phone'), instance.inner_ip)
                    #发送回收成功邮件
                    send_share_release_mail(mail_data)
                # else:
                #     msg = "vpn账号：%s 不存在,不做清除vpn资源操作" % instance.vpn_user_name
                #     logger.error(msg)
                #     ct.send_sms_control('NoLimit', msg, '13681919346')
            else:
                print("还未实现的暂不自动处理")
        # elif instance.__original_other_msg != instance.other_msg:
        #     print("other_msg,发生变化！", instance.other_msg)
        else:
            print("别的变化do nothing")
