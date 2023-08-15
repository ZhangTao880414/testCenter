from rest_framework import serializers
from rest_framework.utils import model_meta
from myapps.tora_monitor import models as mmodels


class MonitorJob_Serializers(serializers.ModelSerializer):

    class Meta:
        model = mmodels.MonitorJob
        fields = '__all__'
    
    def update(self, instance, validated_data):
        serializers.raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        print("调用自定义的Update！！！！")
        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

class DiskMonitorData_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = mmodels.DiskMonitorData
        fields = '__all__'

class MemMonitorData_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = mmodels.MemMonitorData
        fields = '__all__'

class NodeTradeInfo_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = mmodels.NodeTradeInfo
        fields = '__all__'

class SmsControlData_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = mmodels.SmsControlData
        fields = '__all__'

class SmsRecordData_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = mmodels.SmsRecordData
        fields = '__all__'

class ToraDatabaseMonitorCfg_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = mmodels.ToraDatabaseMonitorCfg
        fields = '__all__'

class ipmiInfoData_Serializers(serializers.ModelSerializer):

    class Meta:
        model = mmodels.ipmiInfoData
        fields = '__all__'


class FpgaMonitorData_Serializers(serializers.ModelSerializer):

    operator = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = mmodels.FpgaMonitorData
        fields = '__all__'