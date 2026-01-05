# 后端（Backend）— Django REST 框架详解

## 项目定位与技术栈

### 核心框架
- **框架**：Django 5.2 + Django REST Framework（DRF 3.16）
- **认证**：Simple JWT（`rest_framework_simplejwt`）— 支持 Access & Refresh Token
- **文档**：drf-spectacular — OpenAPI 3.0 / Swagger UI
- **验证码**：django-simple-captcha — 图形验证码
- **数据库**：SQLite（开发默认），支持切换 MySQL/PostgreSQL
- **内置特性**：统一返回格式、统一异常包装、自动分页、软删除、审计字段

### 关键依赖版本
```
Django 5.2.8
djangorestframework 3.16.1
djangorestframework-simplejwt 5.5.1
drf-spectacular 0.27.1
django-simple-captcha 0.6.2
Pillow 12.0.0
```

## 快速开发

### 环境与运行
```powershell
# 创建虚拟环境（Windows）
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 迁移数据库
python manage.py migrate

# 初始化系统数据（可选，会创建默认账号）
python manage.py init_system

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 访问
- 接口文档：http://localhost:8000/api/docs/
- API Schema：http://localhost:8000/api/schema/
- 默认账号（初始化后）：`admin/admin123`、`test/test123`

## 目录结构与职责

### 项目根目录
```
backend/
├── config/                   # 项目全局配置
│   ├── settings.py          # Django 配置（已配置好 REST、JWT、异常处理、分页等）
│   ├── urls.py              # 总 URL 路由（OpenAPI、Swagger、API 入口、前端 SPA）
│   ├── wsgi.py              # WSGI 应用入口（生产）
│   └── asgi.py              # ASGI 应用入口（异步）
├── apps/                    # 业务应用
│   ├── system/              # 系统核心模块（用户、角色、部门、菜单、字典、配置等）
│   ├── monitor/             # 监控模块（日志、性能等）
│   └── common/              # 通用工具（异常、分页、权限、Mixin 等）
├── utils/                   # 工具函数（Excel 导入导出等）
├── db.sqlite3              # SQLite 数据库（开发环境）
├── manage.py               # Django 管理脚本
├── requirements.txt        # Python 依赖
└── README.md              # 本文件
```

### `apps/system/` 详解

#### 模型层（models.py）
定义业务数据模型与通用基类：

**通用基类 `BaseModel`**（所有业务模型的父类）
- `create_by`：创建者
- `update_by`：更新者
- `create_time`：创建时间（自动设置）
- `update_time`：更新时间（自动更新）
- `del_flag`：软删除标记（'0'=正常，'1'=删除）
- 提供多个 Index 优化查询

**核心业务模型**

1. **用户 `User`** — 扩展 Django AbstractUser
   - 字段：`nick_name`、`phonenumber`、`sex`、`avatar`、`status`、`dept_id`（部门）等
   - 通过 `UserRole` 关联角色；通过 `UserPost` 关联岗位
   - 表名：`sys_user`

2. **部门 `Dept`** — 树形组织结构
   - 字段：`dept_id`、`parent_id`（父部门）、`ancestors`（祖级）、`order_num`（排序）、`leader`（负责人）、`phone`、`email`、`status`
   - 表名：`sys_dept`

3. **角色 `Role`** — 权限与数据范围定义
   - 字段：`role_id`、`role_name`、`role_key`、`role_sort`、`data_scope`（数据范围类型）、`status`
   - `data_scope` 支持：全部、自定义部门、本部门、本部门及以下、仅本人
   - 表名：`sys_role`

4. **岗位 `Post`** — 工作岗位
   - 字段：`post_id`、`post_code`、`post_name`、`post_sort`、`status`
   - 表名：`sys_post`

5. **菜单 `Menu`** — 前端路由与权限标识生成
   - 字段：`menu_id`、`parent_id`（树形）、`menu_name`、`path`（路由）、`component`（Vue 组件）、`route_name`、`menu_type`（目录/菜单/按钮）、`visible`、`status`、`perms`（权限标识）、`icon`
   - 前端通过 `getRouters` 接口获取并构建动态路由
   - 表名：`sys_menu`

6. **关联表**
   - `UserRole`：用户-角色绑定（`sys_user_role`）
   - `UserPost`：用户-岗位绑定（`sys_user_post`）
   - `RoleMenu`：角色-菜单绑定（`sys_role_menu`），控制角色权限

7. **字典 `DictType` / `DictData`** — 系统枚举与选项
   - `DictType`：字典分类（如性别、状态等）
   - `DictData`：具体字典值（如：'0'=男，'1'=女）
   - 支持缓存，API 提供快速查询：`GET /api/system/dict/data/type/{dictType}`
   - 表名：`sys_dict_type`、`sys_dict_data`

8. **配置 `Config`** — 系统参数
   - 字段：`config_id`、`config_name`、`config_key`、`config_value`、`config_type`（系统内置标记）
   - 通过 `config_key` 快速查询：`GET /api/system/config/configKey/{configKey}`
   - 支持缓存，API 提供刷新：`DELETE /api/system/config/refreshCache`
   - 表名：`sys_config`

9. **公告 `Notice`** — 通知与公告
   - 字段：`notice_id`、`notice_title`、`notice_type`（通知/公告）、`notice_content`、`status`
   - 表名：`sys_notice`

#### 序列化层（serializers.py）
负责请求/响应数据的校验与转换：
- 支持驼峰命名自动转换（前端发送 `nickName` 自动映射到 `nick_name`）
- 为序列化字段合并公共字段（如 `createTime` 等）
- 自定义验证逻辑（如用户名唯一性）

#### 视图层（views/）
通过 ViewSet + Router 自动生成 REST 接口。

**基础视图类 `BaseViewSet`**（`views/core.py`）
- 继承 `BaseViewMixin` + `viewsets.ModelViewSet`
- 内置 CRUD 方法的统一包装：
  - `list()`：返回 `{code, msg, rows, total}`
  - `create()`：新增，触发审计日志
  - `retrieve()`：详情，返回单个对象
  - `update()`：修改，触发审计日志
  - `destroy()`：删除，默认走软删除（设置 `del_flag='1'`）
- `get_queryset()` 自动过滤软删除记录（`del_flag='0'`）
- 支持前端 PUT 无主键的集合更新（兼容性方法 `update_by_body`）
- `required_roles` 属性支持权限控制（拥有 `admin` 角色自动放行）

**具体视图**
- `UserViewSet`（`views/user.py`）
  - 列表、详情、增删改
  - 自定义操作：重置密码、修改状态、获取部门树、用户资料、头像上传等
  - 过滤支持：用户名、手机、状态、部门、日期范围

- `RoleViewSet`（`views/role.py`）
  - 列表、详情、增删改
  - 自定义操作：修改状态、数据范围分配、部门树选择、用户授权等

- `MenuViewSet`（`views/menu.py`）
  - 列表、详情、增删改
  - 自定义操作：获取菜单树（`treeselect`）、角色菜单树

- `DeptViewSet`（`views/dept.py`）
  - 列表、详情、增删改
  - 自定义操作：获取排除指定部门外的部门列表

- `DictTypeViewSet` 和 `DictDataViewSet`（`views/dict.py`）
  - 字典类型和字典数据的 CRUD
  - 缓存支持：自动缓存和刷新缓存接口

- `ConfigViewSet`（`views/config.py`）
  - 参数配置的 CRUD
  - 按 key 查询、缓存管理

- `PostViewSet`、`NoticeViewSet`：岗位与公告

**核心接口（views/core.py）**
- `LoginView`：登录接口（POST /api/login）
  - 返回 JWT token、刷新 token 等
- `CaptchaView`：生成验证码（GET /api/captchaImage/）
- `GetInfoView`：获取当前用户信息（GET /api/getInfo）
  - 返回 `user`、`roles`、`permissions`、`isDefaultModifyPwd`、`isPasswordExpired` 等
- `LogoutView`：登出（POST /api/logout）
- `GetRoutersView`：获取菜单树作为前端路由（GET /api/getRouters）
  - 后端根据用户角色和菜单权限构建树形结构，前端动态添加路由

#### 权限控制（permission.py）
- `HasRolePermission`：基于角色的权限检查
  - 视图设置 `required_roles = ['admin', 'user']`
  - 拥有指定角色或 `admin` 角色的用户通过
- `HasMenuPermission`：基于菜单权限的检查（备用）

#### 分页（pagination.py）
- `StandardPagination`：统一分页格式
- 分页参数：`pageNum`、`pageSize`
- 响应格式：`{rows: [...], total: 123}`

#### 异常处理（exceptions.py）
- `custom_exception_handler()`：全局异常拦截与统一包装
- 所有异常（包括 DRF ValidationError）统一返回 `{code: HTTP_CODE, message: '错误信息'}`
- 返回 HTTP 200 状态码（兼容前端统一处理）
- 捕获数据库关联错误（ProtectedError 等）、数据库错误、通用异常

#### Mixin 与工具（common/mixins.py）
- `BaseViewMixin`：提供通用响应方法
  - `ok(msg)`、`error(msg)`、`data(data, msg)` 等快速响应
  - `csv_response()`、`excel_response()`：导出 CSV/Excel
- `ExportExcelMixin`：提供 `@action` 导出 Excel 功能

#### URL 路由（urls.py）
使用 DRF 的 `DefaultRouter` 自动生成 REST 路由：
```
GET    /api/system/user/            # 用户列表
POST   /api/system/user/            # 创建用户
GET    /api/system/user/{id}/       # 用户详情
PUT    /api/system/user/{id}/       # 修改用户
DELETE /api/system/user/{id}/       # 删除用户
```

同时兼容前端的集合更新（PUT 无主键）：
```
PUT /api/system/menu               # 批量/集合更新菜单
PUT /api/system/user               # 批量/集合更新用户
```

#### 管理命令（management/commands/init_system.py）
提供一键初始化：
```bash
python manage.py init_system
```
会自动创建：
- 默认账号：`admin/admin123`、`test/test123`
- 系统部门与树形结构
- 系统角色（超级管理员、普通角色等）
- 系统菜单与权限标识
- 字典类型与字典数据

### `apps/common/` 通用工具
- **异常处理**（exceptions.py）：统一异常包装为 `{code, message}`
- **分页**（pagination.py）：标准分页格式
- **权限**（permission.py）：角色与菜单权限检查
- **Mixin**（mixins.py）：响应、导出等通用方法

### `apps/monitor/` 监控模块
- 日志记录、性能监控等（具体实现见源码）

## 核心设计与约定

### 统一返回格式
所有接口都遵循以下格式：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {...},
  "total": 100,  // 列表时包含
  "rows": [...]   // 列表时包含
}
```

### 认证与授权
1. **登录流程**
   - 用户 POST 到 `/api/login` 提交用户名、密码、验证码
   - 后端返回 `access_token` 和 `refresh_token`
   - 前端存储在 localStorage，后续请求在 `Authorization: Bearer {token}` 头中携带

2. **权限检查**
   - 角色权限：`HasRolePermission`，设置 `required_roles = ['admin']`
   - 菜单权限：通过 `Menu.perms` 标识（前端与后端可同步检查）
   - 数据范围：`Role.data_scope` 决定用户可访问的部门数据范围

3. **Token 刷新**
   - Access Token 有效期 8 小时
   - Refresh Token 有效期 1 天
   - 过期时由前端调用刷新接口获取新 token

### 软删除
- 所有模型都包含 `del_flag` 字段（'0'=正常，'1'=删除）
- 查询时自动过滤（`del_flag='0'`）
- 物理删除需显式调用或绕过
- 删除操作自动设置 `del_flag='1'`，保留数据历史

### 审计字段
- `create_by`、`update_by`：记录操作用户
- `create_time`、`update_time`：记录操作时间
- 支持审计日志中间件记录所有修改操作

### 缓存策略
- 字典类型、字典数据、参数配置支持缓存
- API 提供刷新缓存的接口：`DELETE /api/system/dict/type/refreshCache` 等

## 配置详解（config/settings.py）

### REST Framework 配置
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'apps.common.exceptions.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.StandardPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

### JWT 配置
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

### 数据库
- 默认 SQLite（`db.sqlite3`）
- 切换 MySQL：修改 `DATABASES` 配置并安装 `mysqlclient` 或 `PyMySQL`
- 切换 PostgreSQL：修改 `DATABASES` 配置并安装 `psycopg2`

### 静态文件与媒体
- 静态文件：`STATIC_URL = '/static/'`，自动从 `dist/static` 查找（前端构建产物）
- 媒体文件：`MEDIA_URL = '/media/'`，保存在 `media/` 目录

## 常见开发任务

### 1. 添加新的业务模块
1. 在 `apps/` 下创建新应用：`python manage.py startapp myapp`
2. 在 `myapp/models.py` 定义模型，继承 `BaseModel`
3. 在 `myapp/serializers.py` 定义序列化器
4. 在 `myapp/views.py` 定义 ViewSet，继承 `BaseViewSet`
5. 在 `myapp/urls.py` 注册 Router
6. 在 `config/urls.py` 的 `urlpatterns` 中 include 新应用的 URLs
7. 迁移：`python manage.py makemigrations myapp && python manage.py migrate`

### 2. 添加自定义接口
```python
# views.py
from rest_framework.decorators import action

class UserViewSet(BaseViewSet):
    @action(detail=False, methods=['post'])
    def custom_action(self, request):
        # 自定义逻辑
        return self.ok('操作成功')
```
自动生成路由：`POST /api/system/user/custom_action/`

### 3. 添加权限检查
```python
class UserViewSet(BaseViewSet):
    required_roles = ['admin', 'manager']  # 指定允许的角色
```

### 4. 数据导出
使用 `ExportExcelMixin`：
```python
class UserViewSet(ExportExcelMixin, BaseViewSet):
    export_field_label = OrderedDict([
        ('id', 'ID'),
        ('username', '用户名'),
        ('nick_name', '昵称'),
    ])
```
自动生成：`POST /api/system/user/export/`

### 5. 过滤与搜索
在 ViewSet 中使用 `filter_backends` 和 `search_fields`：
```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class UserViewSet(BaseViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status', 'dept_id']
    search_fields = ['username', 'nick_name']
```

## 部署指南

### 生产环境
1. 修改 `settings.py`：
   - `DEBUG = False`
   - `ALLOWED_HOSTS = ['yourdomain.com']`
   - `SECRET_KEY` 更换为安全的密钥
   - 修改数据库为 MySQL/PostgreSQL

2. 收集静态文件：
   ```bash
   python manage.py collectstatic --noinput
   ```

3. 使用 WSGI 应用服务器（如 Gunicorn）：
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
   ```

4. 使用 Nginx 反向代理：
   ```nginx
   location /api/ {
       proxy_pass http://127.0.0.1:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

## 常见问题

### Q: 如何修改数据库为 MySQL？
A: 修改 `config/settings.py` 中的 `DATABASES` 配置，安装 `mysqlclient` 或 `PyMySQL`，然后 `python manage.py migrate`

### Q: 如何扩展用户模型字段？
A: 编辑 `apps/system/models.py` 中的 `User` 模型，添加字段，然后 `python manage.py makemigrations && python manage.py migrate`

### Q: 前端如何获取当前用户权限？
A: 调用 `/api/getInfo` 接口，返回 `roles` 和 `permissions` 数组

### Q: 如何修改 JWT Token 有效期？
A: 修改 `config/settings.py` 中的 `SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']`

## 相关文件链接
- [settings.py](config/settings.py) — 项目配置
- [models.py](apps/system/models.py) — 业务模型
- [views/core.py](apps/system/views/core.py) — 核心视图与接口
- [serializers.py](apps/system/serializers.py) — 数据序列化
- [urls.py](apps/system/urls.py) — API 路由
- [permission.py](apps/system/permission.py) — 权限控制
- [management/commands/init_system.py](apps/system/management/commands/init_system.py) — 初始化脚本
- 参数配置 `Config`：键值型系统参数，带缓存，见 `backend/apps/system/models.py`

## 序列化与约定
- 驼峰输出：所有序列化默认将 `snake_case` 转 `camelCase`，见 `backend/apps/system/serializers.py`
- 公共字段合并：`BaseModelSerializer` 自动添加公共审计/状态字段到 `Meta.fields`，见 `backend/apps/system/serializers.py`
- 集合更新：前端 PUT 无主键的兼容在 `BaseViewSet.update_by_body`，配合 `update_body_serializer_class` 与 `update_body_id_field`，见 `backend/apps/system/views/core.py`

## 视图与路由（/api/）
- 认证与会话
  - `POST /api/login`：登录，返回 `token`，见 `backend/apps/system/views/core.py`
  - `GET /api/captchaImage/`：验证码图片 Base64，见 `backend/apps/system/views/core.py`
  - `GET /api/getInfo`：当前用户信息、角色、权限，见 `backend/apps/system/views/core.py`
  - `POST /api/logout`：退出登录，见 `backend/apps/system/views/core.py`
  - `GET /api/getRouters`：基于菜单生成路由树，见 `backend/apps/system/views/core.py`
- 系统资源（`/api/system/`）
  - 用户 `UserViewSet`：列表/详情/增删改，重置密码、修改状态、个人信息、角色授权，见 `backend/apps/system/views/user.py`
  - 角色 `RoleViewSet`：列表/详情/增删改，改状态、数据范围、授权用户管理，见 `backend/apps/system/views/role.py`
  - 菜单 `MenuViewSet`：列表/详情/增删改，菜单/角色菜单树选择，见 `backend/apps/system/views/menu.py`
  - 部门 `DeptViewSet`：列表/详情/增删改，排除子树列表，见 `backend/apps/system/views/dept.py`
  - 字典类型/数据 `DictTypeViewSet`、`DictDataViewSet`：列表/详情/增删改，类型选项与按类型查询，见 `backend/apps/system/views/dict.py`、`backend/apps/system/views/dict.py`
  - 系统配置 `ConfigViewSet`：列表/详情/增删改，按键查询与刷新缓存，见 `backend/apps/system/views/config.py`
- PUT 集合更新兼容：显式路由兼容如 `PUT /api/system/menu` 等，见 `backend/apps/system/urls.py`

## 返回结构与错误处理
- 成功：`{ code: 200, msg: '操作成功', data | rows, total }`
- 失败：统一 `{ code, message }`，HTTP 状态码通常为 200（前端按 `code` 分支处理），见 `frontend/src/utils/request.js`
- 软删除：`del_flag = '1'`，查询默认 `del_flag = '0'`

## 初始化与示例数据
- 一键初始化（菜单、角色、用户、绑定）：
  ```powershell
  cd backend
  python manage.py migrate
  python manage.py init_system
  ```
- 默认账号（首次初始化）：`admin/admin123`、`test/test123`，见 `backend/apps/system/management/commands/init_system.py`

## 如何运行
- 使用 uv（推荐）
  ```powershell
  cd backend
  uv sync
  ```
  uv 会基于 `pyproject.toml` 与 `uv.lock` 安装依赖并创建虚拟环境（默认 `.venv`）。
- 或使用 venv + pip
  ```powershell
  cd backend
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  ```
- 数据库迁移与启动
  ```powershell
  cd backend
  python manage.py migrate
  python manage.py runserver 0.0.0.0:8000
  ```
- 可选：创建超级用户
  ```powershell
  python manage.py createsuperuser
  ```
- 验证：
  - `POST http://localhost:8000/api/login` 获取 `token`
  - `GET http://localhost:8000/api/docs/` 查看接口文档

## 数据库切换示例（MySQL）
在 `backend/config/settings.py` 修改 `DATABASES`：
```python
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'ruoyi',
    'USER': 'user',
    'PASSWORD': 'password',
    'HOST': '127.0.0.1',
    'PORT': '3306',
    'OPTIONS': { 'charset': 'utf8mb4' }
  }
}
```
然后执行迁移：`python manage.py migrate`

## 二次开发指南
- 新增应用(参考system结构)
  - 在 `apps/` 新建应用，如 `crm`

或者在system应用上扩展功能（不推荐）
- 新增模型
  - 在 `apps/system/models.py` 定义模型，继承 `BaseModel` 获得审计与软删除字段
  - 运行迁移：`python manage.py makemigrations && python manage.py migrate`
- 新增序列化器
  - 在 `apps/system/serializers.py` 添加 `ModelSerializer`，默认输出为驼峰；如需集合更新，定义 `UpdateSerializer`
- 新增视图
  - 在 `apps/system/views/` 新建视图类，继承 `BaseViewSet`
  - 设置 `queryset`、`serializer_class`，如需兼容 PUT 集合更新，设置 `update_body_serializer_class` 与 `update_body_id_field`
  - 可使用 `@audit_log` 记录操作日志，见 `backend/apps/system/common.py`
  - 细粒度权限：在视图设置 `required_roles = ['admin']` 等
- 注册路由
  - 在 `apps/system/urls.py` 使用 `DefaultRouter` 注册资源；必要时显式兼容前端集合更新路由（示例见该文件）
- 初始化数据（可选）
  - 在 `management/commands/` 新增命令脚本，执行初始化（参考 `init_system.py`）
- 缓存与配置
  - 使用 `django.core.cache` 缓存字典/配置结果；键规则示例：`dict_data_by_type:{type}`、`config:{key}`

## 编码约定与建议
- 返回结构统一，尽量复用 `BaseViewSet` 与 `BaseViewMixin`
- 查询默认过滤 `del_flag='0'`，删除使用软删除
- 时间字段统一格式化输出（见 `BaseModelSerializer`）
- 认证路由与资源路由分离：认证在 `core.py`，资源在各自 `ViewSet`
- 生产环境请合理配置 `SECRET_KEY`、`ALLOWED_HOSTS`、数据库凭据与缓存后端，不要暴露敏感信息

## 常见问题
- 登录失败：检查 `rest_framework_simplejwt` 配置与用户状态；查看 `/api/captchaImage/` 与请求体字段
- 接口返回 code=401：前端会触发重新登录提示，见 `frontend/src/utils/request.js`
- 文档无法打开：确认已安装 `drf_spectacular` 且 `urls.py` 已包含文档路由
