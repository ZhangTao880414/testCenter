from django_filters import rest_framework as filters
from myapps.toraapp import models as tmodels



class TaskFlowFilter(filters.FilterSet):
    #'task_status', 'engine_room', 'serial_number', 'IT_checked_number','node_id', 'inner_ip', 'customer', 'create_time'
    task_status = filters.CharFilter(field_name='task_status')
    engine_room = filters.CharFilter(field_name='engine_room')
    serial_number = filters.CharFilter(field_name='serial_number')
    IT_checked_number = filters.CharFilter(field_name='IT_checked_number')
    node_id = filters.CharFilter(field_name='node_id')
    inner_ip = filters.CharFilter(field_name='inner_ip')
    custgroup_name = filters.CharFilter(field_name='custgroup_name', lookup_expr="icontains")
    #创建时间
    created_start_time = filters.DateTimeFilter(field_name='create_time', lookup_expr='gt')
    created_end_time = filters.DateTimeFilter(field_name='create_time', lookup_expr='lt')
   
    class Meta:
        model = tmodels.TaskFlow
        fields = [ 'task_status', 'engine_room', 'serial_number', 'IT_checked_number','node_id', 'inner_ip', 'custgroup_name', 'created_start_time', 'created_end_time']

