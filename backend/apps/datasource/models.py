from django.db import models
from apps.system.models import BaseModel


class DataSource(BaseModel):
    name = models.CharField(max_length=64, verbose_name='数据源名称')
    db_type = models.CharField(max_length=20, verbose_name='数据库类型')  # mysql/postgres/sqlserver/oracle/sqlite
    host = models.CharField(max_length=128, blank=True, default='', verbose_name='主机')
    port = models.IntegerField(default=0, verbose_name='端口')
    db_name = models.CharField(max_length=128, blank=True, default='', verbose_name='数据库名')
    username = models.CharField(max_length=128, blank=True, default='', verbose_name='用户名')
    password = models.CharField(max_length=256, blank=True, default='', verbose_name='密码')
    params = models.TextField(blank=True, default='', verbose_name='连接参数(JSON 或 KV)')
    status = models.CharField(max_length=1, choices=[('0', '正常'), ('1', '停用')], default='0', verbose_name='状态')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'sys_datasource'
        verbose_name = '数据源'
        verbose_name_plural = '数据源'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['db_type']),
            models.Index(fields=['status']),
            models.Index(fields=['del_flag']),
        ]

    def __str__(self):
        return f"{self.name}({self.db_type})"