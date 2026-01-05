from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from django.db.models import Q

from apps.system.views.core import BaseViewSet, BaseViewMixin
from apps.system.permission import HasRolePermission
from apps.system.common import camel_to_snake
from .models import OperLog
from .serializers import OperLogSerializer

import os
import sys
import time
import platform
import socket
import shutil
from datetime import datetime, timedelta


PROCESS_START_TIME = time.time()


def _format_bytes_gb(b):
    try:
        return round(float(b) / (1024 ** 3), 2)
    except Exception:
        return 0.0


def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return '127.0.0.1'


def _get_mem_info():
    total = used = free = usage = 0.0
    try:
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ('dwLength', ctypes.c_ulong),
                ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong),
                ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong),
                ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong),
                ('ullAvailVirtual', ctypes.c_ulonglong),
                ('sullAvailExtendedVirtual', ctypes.c_ulonglong),
            ]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        total_b = int(stat.ullTotalPhys)
        avail_b = int(stat.ullAvailPhys)
        used_b = total_b - avail_b
        total = _format_bytes_gb(total_b)
        used = _format_bytes_gb(used_b)
        free = _format_bytes_gb(avail_b)
        usage = round((used / total) * 100, 2) if total else 0.0
    except Exception:
        try:
            import psutil  # type: ignore
            vm = psutil.virtual_memory()
            total = _format_bytes_gb(vm.total)
            used = _format_bytes_gb(vm.used)
            free = _format_bytes_gb(vm.available)
            usage = round((vm.used / vm.total) * 100, 2) if vm.total else 0.0
        except Exception:
            pass
    return {
        'total': total,
        'used': used,
        'free': free,
        'usage': usage,
    }


def _get_cpu_info():
    cpu_num = os.cpu_count() or 0
    used = sys_p = 0.0
    free = 100.0
    try:
        import psutil  # type: ignore
        used = float(psutil.cpu_percent(interval=0.2))
        sys_p = 0.0
        free = max(0.0, 100.0 - used - sys_p)
    except Exception:
        used = 0.0
        sys_p = 0.0
        free = 100.0
    return {
        'cpuNum': cpu_num,
        'used': round(used, 2),
        'sys': round(sys_p, 2),
        'free': round(free, 2),
    }


def _get_jvm_info():
    name = platform.python_implementation()
    version = platform.python_version()
    start_dt = datetime.fromtimestamp(PROCESS_START_TIME)
    run_delta = datetime.now() - start_dt
    hours, remainder = divmod(run_delta.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    run_time = f"{int(hours)}小时{int(minutes)}分钟"
    home = sys.executable
    input_args = ' '.join(sys.argv)
    return {
        'name': name,
        'version': version,
        'startTime': start_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'runTime': run_time,
        'home': home,
        'inputArgs': input_args,
        'total': 0,
        'used': 0,
        'free': 0,
        'usage': 0,
    }


def _get_sys_files():
    items = []
    try:
        base = os.getcwd()
        total, used, free = shutil.disk_usage(base)
        usage = round((used / total) * 100, 2) if total else 0.0
        items.append({
            'dirName': base,
            'sysTypeName': platform.system(),
            'typeName': 'Fixed',
            'total': f"{_format_bytes_gb(total)}G",
            'free': f"{_format_bytes_gb(free)}G",
            'used': f"{_format_bytes_gb(used)}G",
            'usage': usage,
        })
    except Exception:
        pass
    return items


class ServerView(BaseViewMixin, ViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]

    def get(self, request):
        data = {
            'cpu': _get_cpu_info(),
            'mem': _get_mem_info(),
            'sys': {
                'computerName': platform.node(),
                'osName': f"{platform.system()} {platform.release()}",
                'computerIp': _get_local_ip(),
                'osArch': platform.machine(),
                'userDir': os.getcwd(),
            },
            'jvm': _get_jvm_info(),
            'sysFiles': _get_sys_files(),
        }
        return self.data(data)


class OnlineViewSet(BaseViewMixin, ViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]

    @action(detail=False, methods=['get'], url_path='list')
    def list_action(self, request):
        ipaddr = request.query_params.get('ipaddr', '')
        user_name = request.query_params.get('userName', '')
        ua = request.META.get('HTTP_USER_AGENT', '')
        token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        user = getattr(request, 'user', None)
        dept_name = ''
        try:
            from apps.system.models import Dept
            if user and getattr(user, 'dept_id', None):
                d = Dept.objects.filter(dept_id=user.dept_id).first()
                dept_name = d.dept_name if d else ''
        except Exception:
            pass
        rows = []
        if user and getattr(user, 'username', None):
            if (not user_name) or (user.username.find(user_name) >= 0):
                row = {
                    'tokenId': token or '',
                    'userName': user.username,
                    'deptName': dept_name,
                    'ipaddr': request.META.get('REMOTE_ADDR', ''),
                    'loginLocation': '',
                    'os': platform.system(),
                    'browser': ua,
                    'loginTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }
                if (not ipaddr) or (row['ipaddr'].find(ipaddr) >= 0):
                    rows.append(row)
        # return Response({'code': 200, 'msg': '操作成功', 'rows': rows, 'total': len(rows)})
        return self.raw_response({'code': 200, 'msg': '操作成功', 'rows': rows, 'total': len(rows)})

    @action(methods=['DELETE'], detail=False, url_path='force-logout')
    def destroy_by_token(self, request, *args, **kwargs):
        return self.ok('操作成功')


class OperLogViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    serializer_class = OperLogSerializer
    queryset = OperLog.objects.all().order_by('-oper_time')

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request
        title = request.query_params.get('title', '')
        oper_ip = request.query_params.get('operIp', '')
        oper_name = request.query_params.get('operName', '')
        business_type = request.query_params.get('businessType', '')
        status_v = request.query_params.get('status', '')
        begin = request.query_params.get('beginTime') or request.query_params.get('params[beginTime]')
        end = request.query_params.get('endTime') or request.query_params.get('params[endTime]')

        if title:
            qs = qs.filter(title__icontains=title)
        if oper_ip:
            qs = qs.filter(oper_ip__icontains=oper_ip)
        if oper_name:
            qs = qs.filter(oper_name__icontains=oper_name)
        if business_type != '' and business_type is not None:
            try:
                qs = qs.filter(business_type=int(business_type))
            except Exception:
                pass
        if status_v != '' and status_v is not None:
            try:
                qs = qs.filter(status=int(status_v))
            except Exception:
                pass
        if begin:
            try:
                from datetime import datetime
                dt = datetime.strptime(begin, '%Y-%m-%d %H:%M:%S')
                qs = qs.filter(oper_time__gte=dt)
            except Exception:
                pass
        if end:
            try:
                from datetime import datetime
                dt = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                qs = qs.filter(oper_time__lte=dt)
            except Exception:
                pass

        order_by_column = request.query_params.get('orderByColumn', '')
        is_asc = request.query_params.get('isAsc', '')
        if order_by_column:
            col = camel_to_snake(order_by_column)
            if is_asc == 'descending':
                col = '-' + col
            qs = qs.order_by(col)
        else:
            qs = qs.order_by('-oper_time')
        return qs

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get(self.lookup_field or 'pk')
        if pk and isinstance(pk, str) and ',' in pk:
            ids = [int(i) for i in pk.split(',') if i.isdigit()]
            Model = self.get_queryset().model
            try:
                objs = Model.objects.filter(oper_id__in=ids)
                if hasattr(Model, 'del_flag'):
                    objs.update(del_flag='1')
                else:
                    objs.delete()
                return self.ok('操作成功')
            except Exception:
                return self.error('批量删除失败')
        return super().destroy(request, *args, **kwargs)

    @action(methods=['DELETE'], detail=False, url_path='clean')
    def clean(self, request, *args, **kwargs):
        try:
            Model = self.get_queryset().model
            Model.objects.all().delete()  # 直接删除所有数据，不考虑软删除
            # if hasattr(Model, 'del_flag'):
            #     Model.objects.update(del_flag='1')
            # else:
            #     Model.objects.all().delete()
            return self.ok('操作成功')
        except Exception:
            return self.error('清空失败')

    @action(methods=['POST'], detail=False, url_path='export')
    def export(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        rows = serializer.data
        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = '操作日志'
            headers = [
                '日志编号','系统模块','操作类型','操作人员','操作地址','操作状态','操作时间','消耗时间',
                '请求地址','请求方式','操作方法','请求参数','返回参数','异常信息','登录地点','部门名称'
            ]
            ws.append(headers)
            for r in rows:
                ws.append([
                    r.get('operId'), r.get('title'), r.get('businessType'), r.get('operName'), r.get('operIp'),
                    r.get('status'), r.get('operTime'), r.get('costTime'), r.get('operUrl'), r.get('requestMethod'),
                    r.get('method'), r.get('operParam'), r.get('jsonResult'), r.get('errorMsg'), r.get('operLocation'),
                    r.get('deptName')
                ])
            return self.excel_response('operlog.xlsx', wb)
        except Exception as e:
            return self.error(f'导出失败：{e}')
