from rest_framework import serializers
from myapps.toraapp import models
from django.contrib.auth.models import User
import logging
logger = logging.getLogger('django')



class UserSerializer(serializers.ModelSerializer):
    #Users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = User
        fields = '__all__'


class ToraCustomer_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = models.ToraCustomer
        fields = '__all__'
        #fields = ('id', 'customer_no', 'customer_name', 'company_name', 
        #          'address', 'phone', 'email', 'status', 'comment', 'operator')


class ShelfMachine_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = models.ShelfMachine
        fields = '__all__'


class TaskFlow_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')
    modify_oper = serializers.ReadOnlyField(source='modify_oper.username')
    customer = serializers.ReadOnlyField(source='customer.id')
    #custgroup_name = serializers.ReadOnlyField(source='custgroup_name')
    #custggggname = serializers.ReadOnlyField(source='custgroup_name.custgroup_name')

    class Meta:
        model = models.TaskFlow
        fields = '__all__'

    def validate(self, attrs):
        print("attrs:", attrs)
        #上架完成
        if attrs.get("task_type") == '1' and attrs.get("task_status") == '1':
            print("任务完成更新前校验！")
            #print(attrs.get("inner_ip"),attrs.get("cabinet"),attrs.get("unit"),attrs.get("vpn_user_name"), attrs.get("sys_user_name"), attrs.get("sys_user_passwd"))
            if attrs.get("purpose") in ['1','2']:
                verify_flag = (attrs.get("serial_number") == None or attrs.get("assert_type") == None or attrs.get("server_brand") == None or attrs.get("server_model") == None \
                            or attrs.get("inner_ip") == None or attrs.get("cabinet") == None or attrs.get("unit") == None or attrs.get("vpn_user_name") == ''\
                            or attrs.get("sys_user_name") == None or attrs.get("IT_checked_number") == None)
            else:
                verify_flag = (attrs.get("serial_number") == None or attrs.get("assert_type") == None or attrs.get("server_brand") == None or attrs.get("server_model") == None \
                        or attrs.get("inner_ip") == None or attrs.get("cabinet") == None or attrs.get("unit") == None or attrs.get("IT_checked_number") == None)
            # if attrs.get("inner_ip") == '' and attrs.get("cabinet") == '' and attrs.get("unit") == '' and attrs.get("os") == '' 
            #         and attrs.get("vpn_user_name") == '' and attrs.get("sys_user_name") == '' and attrs.get("sys_user_passwd") == '':
            if verify_flag:  
                raise serializers.ValidationError('置完成状态时服务器硬件信息，机柜号，内网IP，系统版本，vpn,系统用户信息必填！')       
            if attrs.get("access_finished") != '1':
                raise serializers.ValidationError('网络授权完成状态未置完成，不能更新任务状态为已完成！')
        #下架
        elif attrs.get("task_type") == '2' and attrs.get("serial_number") == '':
            raise serializers.ValidationError('服务器下架时,设备序列号必填！')
        #共享资源回收
        elif attrs.get("task_type") == '6':
            if (attrs.get("inner_ip") == None or attrs.get("sys_user_name") == None or attrs.get("vpn_user_name")) == None :
                raise serializers.ValidationError('inner_ip,vpn_user_name,sys_user_name, 必填！')
        return attrs


class NodeInfo_Serializers(serializers.ModelSerializer):

    class Meta:
        model = models.NodeInfo
        fields = '__all__'


class ToraService_Serializers(serializers.ModelSerializer):

    machine = serializers.ReadOnlyField(source='machine.inner_ip')

    class Meta:
        model = models.ToraService
        fields = '__all__'



class SystemUserInfo_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')
    customer = serializers.ReadOnlyField(source='customer.custgroup')

    class Meta:
        model = models.SystemUserInfo
        fields = '__all__'
        # fields = ('id', 'engine_room', 'inner_ip', 'sys_user_name', 
        #           'sys_user_passwd', 'cur_status', 'nsight_user', 'operator')

class VpnUserInfo_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')
    customer = serializers.ReadOnlyField(source='customer.custgroup')

    class Meta:
        model = models.VpnUserInfo
        fields = '__all__'


class VpnCfgInfo_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = models.VpnCfgInfo
        fields = '__all__'


class TradeNode_Serializers(serializers.ModelSerializer):

    customer = serializers.ReadOnlyField(source='customer.custgroup')

    class Meta:
        model = models.TradeNode
        fields = '__all__'


class ToraMq_Serializers(serializers.ModelSerializer):

    class Meta:
        model = models.ToraMq
        fields = '__all__'


class ToraMqGroup_Serializers(serializers.ModelSerializer):

    class Meta:
        model = models.ToraMqGroup
        fields = '__all__'


class ShareServerInfo_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')
    machine = serializers.ReadOnlyField(source='machine.inner_ip')

    class Meta:
        model = models.ShareServerInfo
        fields = '__all__'


class UserProfile_Serializers(serializers.ModelSerializer):
    #user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = models.UserProfile
        fields = '__all__'


class NodeDetailInfo_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = models.NodeDetailInfo
        fields = '__all__'


class UpgradeTask_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')
    business = serializers.SerializerMethodField()

    class Meta:
        model = models.UpgradeTask
        fields = '__all__'
    
    def get_business(self, obj):
        return obj.get_business_display()


class Area_Serializers(serializers.ModelSerializer):

    #operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = models.Area
        fields = '__all__'


class GloblePara_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')
    modify_oper = serializers.ReadOnlyField(source='modify_oper.username')
    
    class Meta:
        model = models.GloblePara
        fields = '__all__'


class AccessApplyInfo_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')
    
    class Meta:
        model = models.AccessApplyInfo
        fields = '__all__'