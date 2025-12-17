from django.db import models

class OperLog(models.Model):
    oper_id = models.BigAutoField(primary_key=True, verbose_name='日志主键')
    title = models.CharField(max_length=50, verbose_name='模块标题')
    business_type = models.IntegerField(default=0, verbose_name='业务类型')
    method = models.CharField(max_length=100, verbose_name='方法名称')
    request_method = models.CharField(max_length=10, verbose_name='请求方式')
    operator_type = models.IntegerField(default=0, verbose_name='操作类别')
    oper_name = models.CharField(max_length=50, verbose_name='操作人员')
    dept_name = models.CharField(max_length=50, verbose_name='部门名称', blank=True, null=True)
    oper_url = models.CharField(max_length=255, verbose_name='请求URL')
    oper_ip = models.CharField(max_length=128, verbose_name='主机地址')
    oper_location = models.CharField(max_length=255, verbose_name='操作地点', blank=True, null=True)
    oper_param = models.TextField(verbose_name='请求参数', blank=True, null=True)
    json_result = models.TextField(verbose_name='返回参数', blank=True, null=True)
    status = models.IntegerField(default=0, verbose_name='操作状态')
    error_msg = models.TextField(verbose_name='错误消息', blank=True, null=True)
    oper_time = models.DateTimeField(verbose_name='操作时间', auto_now_add=True)
    cost_time = models.BigIntegerField(default=0, verbose_name='消耗时间')

    class Meta:
        db_table = 'sys_oper_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-oper_time']


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
