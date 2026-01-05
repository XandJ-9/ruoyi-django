from django.db import models
from django.utils import timezone

from apps.system.models import BaseModel


class OperLog(BaseModel):
    oper_id = models.AutoField(primary_key=True, verbose_name='操作日志ID')
    title = models.CharField(max_length=100, blank=True, default='', verbose_name='系统模块')
    business_type = models.IntegerField(default=0, verbose_name='业务类型')
    method = models.CharField(max_length=200, blank=True, default='', verbose_name='方法名称')
    request_method = models.CharField(max_length=10, blank=True, default='', verbose_name='请求方式')
    operator_type = models.IntegerField(default=0, verbose_name='操作类别')
    oper_name = models.CharField(max_length=50, blank=True, default='', verbose_name='操作人员')
    dept_name = models.CharField(max_length=50, blank=True, default='', verbose_name='部门名称')
    oper_url = models.CharField(max_length=255, blank=True, default='', verbose_name='请求URL')
    oper_ip = models.CharField(max_length=128, blank=True, default='', verbose_name='主机地址')
    oper_location = models.CharField(max_length=255, blank=True, default='', verbose_name='操作地点')
    oper_param = models.TextField(blank=True, default='', verbose_name='请求参数')
    json_result = models.TextField(blank=True, default='', verbose_name='返回参数')
    status = models.IntegerField(default=0, verbose_name='操作状态')
    error_msg = models.TextField(blank=True, default='', verbose_name='错误消息')
    oper_time = models.DateTimeField(default=timezone.now, verbose_name='操作时间')
    cost_time = models.IntegerField(default=0, verbose_name='消耗时间(毫秒)')

    class Meta:
        db_table = 'sys_oper_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        indexes = [
            models.Index(fields=['del_flag']),
            models.Index(fields=['status']),
            models.Index(fields=['oper_time']),
            models.Index(fields=['oper_name']),
            models.Index(fields=['title']),
            models.Index(fields=['business_type']),
        ]

    def __str__(self):
        return f"{self.oper_id}-{self.title}-{self.oper_name}"


class Logininfor(models.Model):
    info_id = models.BigAutoField(primary_key=True, verbose_name='访问ID')
    user_name = models.CharField(max_length=50, verbose_name='用户账号')
    ipaddr = models.CharField(max_length=128, verbose_name='登录IP地址')
    login_location = models.CharField(max_length=255, verbose_name='登录地点', blank=True, null=True)
    browser = models.CharField(max_length=50, verbose_name='浏览器类型', blank=True, null=True)
    os = models.CharField(max_length=50, verbose_name='操作系统', blank=True, null=True)
    status = models.CharField(max_length=1, default='0', verbose_name='登录状态')
    msg = models.CharField(max_length=255, verbose_name='提示消息', blank=True, null=True)
    login_time = models.DateTimeField(verbose_name='访问时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_logininfor'
        verbose_name = '系统登录日志'
        verbose_name_plural = '系统登录日志'
        ordering = ['-login_time']

