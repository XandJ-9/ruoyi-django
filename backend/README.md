# 后端（backend）说明文档

## 项目定位与技术栈
- 框架：Django 5.x + Django REST Framework（DRF）
- 认证：`rest_framework_simplejwt`（JWT）
- 文档：`drf_spectacular`（OpenAPI/Swagger）
- 验证码：`django-simple-captcha`
- 数据库：默认 SQLite，可切换 MySQL/PostgreSQL
- 统一返回格式、统一异常包装、统一分页、软删除与审计字段内置

## 目录结构与职责
- `config/`：项目配置
  - `settings.py`：全局配置（认证、分页、异常、语言、静态资源等），见 `backend/config/settings.py`
  - `urls.py`：URL 总入口（前端入口、REST 路由、文档），见 `backend/config/urls.py`
  - `wsgi.py`、`asgi.py`：部署入口
- `apps/system/`：系统模块（用户、角色、部门、菜单、字典、配置）
  - `models.py`：业务模型与通用基类，见 `backend/apps/system/models.py`
  - `serializers.py`：序列化与校验，驼峰命名转换与公共字段合并，见 `backend/apps/system/serializers.py`
  - `views/`：视图与接口实现，含通用基类 `BaseViewSet`，见 `backend/apps/system/views/core.py`
  - `permission.py`：角色权限控制，见 `backend/apps/system/permission.py`
  - `pagination.py`：分页统一格式，见 `backend/apps/system/pagination.py`
  - `exceptions.py`：异常统一包装 `{code, message}`，见 `backend/apps/system/exceptions.py`
  - `management/commands/init_system.py`：一键初始化菜单、角色、用户与绑定，见 `backend/apps/system/management/commands/init_system.py`
  - `urls.py`：系统 API 路由注册，见 `backend/apps/system/urls.py`
- 根文件
  - `manage.py`：Django 管理命令入口
  - `requirements.txt`、`pyproject.toml`、`uv.lock`：依赖与环境管理

## 配置关键点
- 认证与权限
  - DRF 默认认证：`JWTAuthentication`，见 `backend/config/settings.py`
  - 角色权限：`HasRolePermission` 可在视图上设置 `required_roles`，拥有 `admin` 自动放行，见 `backend/apps/system/permission.py`
- 分页与异常
  - 分页参数：`pageNum`、`pageSize`，返回 `{code, msg, total, rows}`，见 `backend/apps/system/pagination.py`
  - 异常包装：统一为 `{code, message}` 并返回 200 状态码以兼容前端处理，见 `backend/apps/system/exceptions.py`
- 接口文档
  - OpenAPI Schema：`/api/schema/`
  - Swagger UI：`/api/docs/`，见 `backend/config/urls.py`
- 其他
  - 用户模型：`AUTH_USER_MODEL = 'system.User'`，见 `backend/config/settings.py`
  - 软删除：所有模型包含 `del_flag` 字段，删除走软删除，见 `backend/apps/system/models.py` 与 `BaseViewSet.destroy`
  - 语言：`zh-hans`；`USE_TZ = False`；`ALLOWED_HOSTS = ['*']`

## 模型与数据
- 通用基类 `BaseModel`：`create_by`、`update_by`、`create_time`、`update_time`、`del_flag`，见 `backend/apps/system/models.py`
- 用户 `User`：扩展 `AbstractUser`，新增 `nick_name`、`phonenumber`、`sex`、`avatar`、`status`、`dept_id`，见 `backend/apps/system/models.py`
- 角色 `Role``/`用户角色 `UserRole`：用户-角色绑定，见 `backend/apps/system/models.py`、`backend/apps/system/models.py`
- 菜单 `Menu``/`角色菜单 `RoleMenu`：用于生成前端路由与权限标识，见 `backend/apps/system/models.py`、`backend/apps/system/models.py`
- 部门 `Dept`：树形结构（`parent_id`/`order_num`），见 `backend/apps/system/models.py`
- 字典类型 `DictType` 与字典数据 `DictData`：系统枚举配置与选项缓存，见 `backend/apps/system/models.py`、`backend/apps/system/models.py`
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
