from rest_framework import serializers
from apps.system.serializers import BaseModelSerializer
from .models import DataSource

from apps.common.encrypt import encrypt_password, decrypt_password

class DataSourceSerializer(BaseModelSerializer):
    dataSourceId = serializers.IntegerField(source='id')
    dataSourceName = serializers.CharField(source='name')
    dbType = serializers.CharField(source='db_type')
    host = serializers.CharField()
    port = serializers.IntegerField()
    dbName = serializers.CharField(source='db_name')
    username = serializers.CharField()
    password = serializers.SerializerMethodField()
    params = serializers.CharField(required=False, allow_blank=True)
    
    def get_password(self, obj):
        return encrypt_password(obj.password)

    class Meta:
        model = DataSource
        fields = [
            'dataSourceId', 'dataSourceName', 'dbType', 'host', 'port', 'dbName',
            'username', 'password', 'params'
        ]


class DataSourceQuerySerializer(serializers.Serializer):
    dataSourceName = serializers.CharField(required=False, allow_blank=True)
    dbType = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(required=False, choices=['0', '1'])

class DataSourceCreateSerializer(DataSourceSerializer):
    password = serializers.CharField(required=False, allow_blank=True)

class DataSourceUpdateSerializer(DataSourceSerializer):
    password = serializers.CharField(required=False, allow_blank=True)

class DataQuerySerializer(serializers.Serializer):
    sql = serializers.CharField()
    params = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=50)
    offset = serializers.IntegerField(required=False, min_value=0, default=0)
