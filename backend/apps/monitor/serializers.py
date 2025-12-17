from rest_framework import serializers
from apps.system.serializers import PaginationQuerySerializer, BaseModelSerializer
from .models import OperLog, Logininfor

class OperLogSerializer(BaseModelSerializer):
    operId = serializers.IntegerField(source='oper_id', read_only=True)
    title = serializers.CharField()
    businessType = serializers.IntegerField(source='business_type')
    method = serializers.CharField()
    requestMethod = serializers.CharField(source='request_method')
    operatorType = serializers.IntegerField(source='operator_type')
    operName = serializers.CharField(source='oper_name')
    deptName = serializers.CharField(source='dept_name')
    operUrl = serializers.CharField(source='oper_url')
    operIp = serializers.CharField(source='oper_ip')
    operLocation = serializers.CharField(source='oper_location')
    operParam = serializers.CharField(source='oper_param')
    jsonResult = serializers.CharField(source='json_result')
    status = serializers.IntegerField()
    errorMsg = serializers.CharField(source='error_msg')
    operTime = serializers.DateTimeField(source='oper_time', format='%Y-%m-%d %H:%M:%S')
    costTime = serializers.IntegerField(source='cost_time')

    class Meta:
        model = OperLog
        fields = ['operId', 'title', 'businessType', 'method', 'requestMethod', 'operatorType', 
                  'operName', 'deptName', 'operUrl', 'operIp', 'operLocation', 'operParam', 
                  'jsonResult', 'status', 'errorMsg', 'operTime', 'costTime']

class OperLogQuerySerializer(PaginationQuerySerializer):
    title = serializers.CharField(required=False, allow_blank=True)
    operName = serializers.CharField(required=False, allow_blank=True)
    businessType = serializers.IntegerField(required=False)
    status = serializers.IntegerField(required=False)
    beginTime = serializers.DateTimeField(required=False)
    endTime = serializers.DateTimeField(required=False)


class LogininforSerializer(BaseModelSerializer):
    infoId = serializers.IntegerField(source='info_id', read_only=True)
    userName = serializers.CharField(source='user_name')
    ipaddr = serializers.CharField()
    loginLocation = serializers.CharField(source='login_location')
    browser = serializers.CharField()
    os = serializers.CharField()
    status = serializers.CharField()
    msg = serializers.CharField()
    loginTime = serializers.DateTimeField(source='login_time', format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Logininfor
        fields = ['infoId', 'userName', 'ipaddr', 'loginLocation', 'browser', 'os', 
                  'status', 'msg', 'loginTime']

class LogininforQuerySerializer(PaginationQuerySerializer):
    ipaddr = serializers.CharField(required=False, allow_blank=True)
    userName = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    beginTime = serializers.DateTimeField(required=False)
    endTime = serializers.DateTimeField(required=False)
