import json
import time
from datetime import datetime

from django.utils import timezone

from .models import OperLog


SENSITIVE_KEYS = {"password", "pwd", "pass", "secret", "token", "accessToken"}


def _mask_value(key, value):
    if key and key.lower() in SENSITIVE_KEYS:
        return "****"
    return value


def _build_params_snapshot(request):
    try:
        if request.method == 'GET':
            # Query params
            params = {}
            for k, v in request.GET.items():
                params[k] = _mask_value(k, v)
            return json.dumps(params, ensure_ascii=False)
        else:
            # Body params
            try:
                body = request.body.decode('utf-8') if request.body else ''
                # Try json
                try:
                    data = json.loads(body)
                    if isinstance(data, dict):
                        for k in list(data.keys()):
                            data[k] = _mask_value(k, data[k])
                        return json.dumps(data, ensure_ascii=False)
                    return body[:4000]
                except Exception:
                    return body[:4000]
            except Exception:
                return ''
    except Exception:
        return ''


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        # First IP in XFF
        ip = xff.split(',')[0].strip()
        if ip:
            return ip
    return request.META.get('REMOTE_ADDR', '')


def _get_dept_name(user):
    try:
        from apps.system.models import Dept
        if user and getattr(user, 'dept_id', None):
            d = Dept.objects.filter(dept_id=user.dept_id).first()
            return d.dept_name if d else ''
    except Exception:
        pass
    return ''


def _business_type_from_method(method: str) -> int:
    m = (method or '').upper()
    if m == 'GET':
        return 1  # 查询
    if m == 'POST':
        return 2  # 新增
    if m == 'PUT':
        return 3  # 修改
    if m == 'DELETE':
        return 4  # 删除
    return 0      # 其他


class OperLogMiddleware:
    """
    记录后端接口的操作日志：请求方法、路径、用户、参数、响应结果等。
    仅记录以 /data-api/ 开头的接口，避免前端静态资源噪音。
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 仅记录 API 路径
        path = request.path or ''
        if not path.startswith('/data-api/'):
            return self.get_response(request)

        start_ts = time.time()
        error_msg = ''
        response = None
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            error_msg = str(e)[:2000]
            # 继续抛出异常，让 DRF 统一处理
            raise
        finally:
            try:
                cost_time = int((time.time() - start_ts) * 1000)
                user = getattr(request, 'user', None)

                # 解析路由匹配信息
                view_name = ''
                try:
                    rm = getattr(request, 'resolver_match', None)
                    if rm:
                        if rm.view_name:
                            view_name = rm.view_name
                        elif rm.func:
                            view_name = getattr(rm.func, '__name__', '')
                except Exception:
                    pass

                # 构造 title：取 /data-api/ 后第一段作为模块名
                try:
                    # /data-api/<module>/...
                    segs = path[len('/data-api/'):].split('/')
                    title = segs[0] if segs and segs[0] else 'data-api'
                except Exception:
                    title = 'data-api'

                # 请求参数快照
                oper_param = _build_params_snapshot(request)

                # 响应结果（尽量提取成功/失败与部分内容）
                status_code = getattr(response, 'status_code', 500)
                status_val = 0
                json_result = ''
                try:
                    if hasattr(response, 'data'):
                        # DRF Response
                        data = response.data
                        # 简化判断成功
                        code_in_data = None
                        try:
                            code_in_data = int(data.get('code'))
                        except Exception:
                            pass
                        status_val = 0 if status_code == 200 and code_in_data == 200 and not error_msg else 1
                        json_result = json.dumps(data, ensure_ascii=False)[:4000]
                    elif hasattr(response, 'content'):
                        content = ''
                        try:
                            content = response.content.decode('utf-8', errors='ignore')
                        except Exception:
                            pass
                        status_val = 0 if status_code == 200 and not error_msg else 1
                        json_result = content[:2000]
                    else:
                        status_val = 1 if error_msg else 0
                except Exception:
                    status_val = 1 if error_msg else 0

                # 保存操作日志
                OperLog.objects.create(
                    title=title,
                    business_type=_business_type_from_method(request.method),
                    method=view_name or request.method,
                    request_method=request.method,
                    operator_type=0,
                    oper_name=(getattr(user, 'username', '') or ''),
                    dept_name=_get_dept_name(user),
                    oper_url=path,
                    oper_ip=_get_client_ip(request),
                    oper_location='',
                    oper_param=oper_param,
                    json_result=json_result,
                    status=status_val,
                    error_msg=error_msg,
                    oper_time=timezone.now(),
                    cost_time=cost_time,
                    create_by=(getattr(user, 'username', '') or ''),
                    update_by=(getattr(user, 'username', '') or ''),
                )
            except Exception:
                # 避免日志写入影响主流程
                pass