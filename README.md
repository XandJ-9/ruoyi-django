# RuoYi Django — 项目概览与快速上手

这是一个基于 RuoYi 前端模板的后端实现示例（Django + DRF），并包含配套的 Vue 3 前端（Vite + Element Plus）。

核心要点
- 后端：Django 5、Django REST Framework、Simple JWT、drf-spectacular（OpenAPI）。
- 前端：Vue 3、Vite、Element Plus、Pinia。前后端分离，API 以 `/api/` 前缀暴露。
- 默认开发数据库：SQLite（`backend/db.sqlite3`），可切换为 MySQL/Postgres（修改 `config/settings.py`）。

快速启动（Windows）

1) 后端（开发）

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py init_system    # 可选：初始化默认账号与菜单
python manage.py runserver 0.0.0.0:8000
```

2) 前端（开发）

```powershell
cd frontend
npm install
npm run dev
```

访问
- 后端接口文档（OpenAPI/Swagger）：http://localhost:8000/api/docs/
- 前端开发服务器（默认 Vite 端口）：http://localhost:5173/

目录速览
- `backend/`：Django 项目与 apps（`apps/system` 为主要示例模块）。
- `frontend/`：Vue 3 应用源码，入口在 `src/`。

常见文件
- `backend/requirements.txt`：Python 依赖。
- `frontend/package.json`：前端依赖与脚本。
- `backend/manage.py`：Django 管理脚本。

环境与配置
- 前端通过 `VITE_APP_BASE_API` 指定 API 基址（见 `frontend/.env.*`）。
- 后端配置位于 `backend/config/`（包含 `settings.py`、`urls.py` 等）。

初始化账户（示例）
- 使用 `python manage.py init_system` 可创建默认账号（如 `admin`）。

构建与发布
- 前端构建：

```powershell
cd frontend
npm run build:prod
```

- 将构建产物部署到静态服务器，或由后端静态服务托管。

开发与贡献
- 若要新增后端模块，请在 `backend/apps/` 下创建新的 Django app，并在 `backend/config/urls.py` 中注册路由。
- 保持统一的接口返回格式（`{code,msg,data}`）与异常处理方式，便于前端无缝对接。

许可证
- 前端使用的 `package.json` 指明项目采用 MIT 许可证，仓库中未包含其他许可证说明，请根据需要补充。

更多信息
- 若需更详细的后端 API 或模块说明，请查看 `backend/apps/system` 下的各个模块源码（`models.py`、`views/`、`serializers.py`、`urls.py`）。

文件： [backend/README.md](backend/README.md)（如存在）包含更细的后端说明与管理命令示例。


