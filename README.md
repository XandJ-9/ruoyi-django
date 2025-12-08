# RuoYi Django 全栈项目介绍

## 概览
- 前后端分离的管理系统：后端 `Django + DRF + SimpleJWT`，前端 `Vue 3 + Vite + Element Plus`。
- 根目录包含两个子项目：`backend/` 与 `frontend/`，均可独立开发与运行。
- 提供统一的接口返回格式，内置分页、异常包装、角色权限与菜单路由生成，兼容 RuoYi 前端。

## 目录结构（关键项）
- `backend/`：后端 Django 项目
  - `config/`：项目配置（`settings.py`、`urls.py`、`wsgi.py`、`asgi.py`）
  - `apps/system/`：系统业务模块（用户、角色、部门、菜单、字典、配置）
  - `manage.py`：管理命令入口
  - `requirements.txt`、`pyproject.toml`：依赖与元信息
- `frontend/`：前端应用（RuoYi Vue 3）
  - `src/`：业务源码（`views/`、`components/`、`api/`、`store/`、`utils/`）
  - `.env.*`：环境变量（`VITE_APP_BASE_API` 等）
  - `package.json`：脚本与依赖
- `README.md`：当前说明文档

## 后端说明[backend/README.md]
- 框架与配置
  - 认证：`JWT`（`rest_framework_simplejwt`），见 `backend/config/settings.py`。
  - 异常处理：统一包装为 `{code, message}`，见 `backend/apps/system/exceptions.py`。
  - 分页：页码 `pageNum`，大小 `pageSize`，见 `backend/apps/system/pagination.py`。
  - 用户模型：自定义 `AUTH_USER_MODEL = 'system.User'`，见 `backend/config/settings.py`。
- URL 与文档
  - 根 URL 配置见 `backend/config/urls.py`：接口前缀为 `/api/`；内置 `OpenAPI` 与 `Swagger` 文档：`/api/schema/`、`/api/docs/`。
- 认证与会话
  - 登录：`POST /api/login`（返回 `token`），逻辑在 `LoginView`，见 `backend/apps/system/views/core.py`。
  - 验证码：`GET /api/captchaImage/`，见 `backend/apps/system/views/core.py`。
  - 当前用户信息：`GET /api/getInfo`（含 `roles`/`permissions`），见 `backend/apps/system/views/core.py`。
  - 登出：`POST /api/logout`，见 `backend/apps/system/views/core.py`。
  - 菜单路由：`GET /api/getRouters`，后端按 `Menu` 构建树并输出路由，见 `backend/apps/system/views/core.py`。
- 权限控制
  - 角色权限类 `HasRolePermission` 支持在视图设置 `required_roles`，并自动放行拥有 `admin` 的用户，见 `backend/apps/system/permission.py`。
- 通用视图基类
  - `BaseViewSet` 封装列表、详情、创建、更新、软删除、集合更新（PUT 无主键），统一返回格式，见 `backend/apps/system/views/core.py`。

## 业务模型（apps/system/models.py）
- 用户 `User`：扩展 `AbstractUser`，含 `nick_name`、`phonenumber`、`sex`、`avatar`、`status`、`dept_id` 等，见 `backend/apps/system/models.py`。
- 部门 `Dept`：树形结构，字段 `parent_id`、`order_num`、`status` 等，见 `backend/apps/system/models.py`。
- 角色 `Role`：`role_key`、`data_scope`、`status` 等，见 `backend/apps/system/models.py`。
- 用户-角色 `UserRole`：用户与角色绑定，见 `backend/apps/system/models.py`。
- 菜单 `Menu`：用于前端路由与权限标识，见 `backend/apps/system/models.py`。
- 角色-菜单 `RoleMenu`：角色与菜单绑定，见 `backend/apps/system/models.py`。
- 字典类型 `DictType` 与字典数据 `DictData`：配置枚举与选项，见 `backend/apps/system/models.py`、`backend/apps/system/models.py`。
- 参数配置 `Config`：系统配置键值，见 `backend/apps/system/models.py`。

## API 资源与路由（`/api/system/`）
- 路由注册见 `backend/apps/system/urls.py`：`user`、`menu`、`role`、`dept`、`dict/type`、`dict/data`、`config`。
- 用户 `UserViewSet`，见 `backend/apps/system/views/user.py`
  - 列表/详情/增删改，支持条件过滤（用户名、手机号、状态、部门、时间范围）。
  - 操作：`PUT /user/resetPwd`、`PUT /user/changeStatus`、`GET /user/deptTree`、`GET /user/profile`、`PUT /user/updateProfile`、`PUT /user/updatePwd`、`POST /user/avatar`、`GET /user/authRole/{userId}`、`PUT /user/authRole`。
- 角色 `RoleViewSet`，见 `backend/apps/system/views/role.py`
  - 列表/详情/增删改，支持条件过滤（角色名、权限键、状态、时间范围）。
  - 操作：`PUT /role/changeStatus`、`PUT /role/dataScope`、`GET /role/deptTree/{roleId}`、`GET /role/authUser/allocatedList`、`GET /role/authUser/unallocatedList`、`PUT /role/authUser/cancel`、`PUT /role/authUser/cancelAll`、`PUT /role/authUser/selectAll`。
- 菜单 `MenuViewSet`，见 `backend/apps/system/views/menu.py`
  - 列表/详情/增删改，支持条件过滤（菜单名、状态）。
  - 操作：`GET /menu/treeselect`、`GET /menu/roleMenuTreeselect/{roleId}`。
- 部门 `DeptViewSet`，见 `backend/apps/system/views/dept.py`
  - 列表/详情/增删改，支持条件过滤（部门名、状态）。
  - 操作：`GET /dept/list/exclude/{deptId}`。
- 字典类型 `DictTypeViewSet` 与字典数据 `DictDataViewSet`，见 `backend/apps/system/views/dict.py`、`backend/apps/system/views/dict.py`
  - 列表/详情/增删改，带缓存：`GET /dict/type/optionselect`、`DELETE /dict/type/refreshCache`、`GET /dict/data/type/{dictType}`。
- 参数配置 `ConfigViewSet`，见 `backend/apps/system/views/config.py`
  - 列表/详情/增删改，缓存 `config:{configKey}`，`GET /config/configKey/{configKey}`、`DELETE /config/refreshCache`。
- 集合更新（前端兼容 PUT 无主键）：如 `PUT /system/menu` 等已在 `backend/apps/system/urls.py` 显式兼容。

## 初始化数据（推荐）
- 提供管理命令一键初始化菜单、角色、用户与绑定，见 `backend/apps/system/management/commands/init_system.py`。
- 运行：
  ```powershell
  cd backend
  python manage.py migrate
  python manage.py init_system
  ```
- 默认账号：`admin/admin123`、`test/test123`（如首次初始化），见 `backend/apps/system/management/commands/init_system.py`。

## 前端说明[frontend/README.md]
- 环境变量：`
  frontend/.env.development` 使用 `VITE_APP_BASE_API='/dev-api'`（见 `frontend/.env.development`）。构建产物可通过后端静态目录提供或独立部署。
- 启动开发：
  ```powershell
  cd frontend
  npm install
  npm run dev
  ```
- 前端请求基址读取 `VITE_APP_BASE_API`，统一在 `axios` 实例中设置，见 `frontend/src/utils/request.js`。

## 本地运行（建议顺序）
- 后端（8000）
  ```powershell
  cd backend
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py init_system  # 可选，初始化数据
  python manage.py runserver 0.0.0.0:8000
  ```
- 前端（默认 5173）
  ```powershell
  cd frontend
  npm install
  npm run dev
  ```
- 接口文档：浏览器访问 `http://localhost:8000/api/docs/` 查看接口与模型。

## 设计要点与约定
- 统一返回：`{ code, msg, data | rows, total }`，前端在 `frontend/src/utils/request.js` 处按 `code` 处理。
- 软删除：所有业务模型包含 `del_flag` 字段，删除走软删除，见 `backend/apps/system/models.py` 与 `BaseViewSet.destroy`。
- 路由生成：菜单 `Menu` 的树形结构映射为前端路由，见 `backend/apps/system/views/core.py`。
- 权限模型：基于角色 `role_key` 与菜单 `perms`，视图可指定 `required_roles` 做粗粒度控制。

如需扩展业务模块，可在 `apps/` 下新增应用，并在 `config/urls.py` 注册路由；保持统一返回格式与异常处理，前端即可无缝对接。

