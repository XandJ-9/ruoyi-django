# 前端（Frontend）— Vue 3 + Element Plus 详解

## 项目定位与技术栈

### 核心框架
- **框架**：Vue 3.5.16（Composition API）
- **UI 库**：Element Plus 2.10.7 — 企业级组件库
- **构建工具**：Vite 6.3.5 — 极速前端构建
- **路由**：Vue Router 4.5.1 — 前端路由管理
- **状态管理**：Pinia 3.0.2 — 轻量级状态库
- **HTTP 客户端**：Axios 1.9.0 + 请求拦截与响应处理
- **样式**：SCSS/Sass（sass-embedded 1.89.1）
- **构建优化**：vite-plugin-svg-icons、vite-plugin-compression

### 关键依赖版本
```json
{
  "vue": "3.5.16",
  "element-plus": "2.10.7",
  "vite": "6.3.5",
  "vue-router": "4.5.1",
  "pinia": "3.0.2",
  "axios": "1.9.0"
}
```

## 快速开发

### 环境与运行
```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器（Vite 默认 5173 端口）
npm run dev

# 构建生产版本
npm run build:prod

# 构建测试版本
npm run build:stage

# 预览构建结果
npm preview
```

### 访问
- 前端开发服务器：http://localhost:5173/
- 后端 API 文档：http://localhost:8000/api/docs/
- 登录账号（初始化后）：`admin/admin123` 或 `test/test123`

## 目录结构

### 项目根目录
```
frontend/
├── public/                  # 公共资源
├── src/                     # 源代码
│   ├── App.vue             # 根组件
│   ├── main.js             # 应用入口
│   ├── permission.js       # 路由权限守卫
│   ├── settings.js         # 全局设置
│   ├── api/                # API 接口定义
│   ├── assets/             # 静态资源（样式、图片、图标）
│   ├── components/         # 全局通用组件
│   ├── directive/          # 自定义指令（权限控制）
│   ├── layout/             # 布局组件
│   ├── plugins/            # 插件配置
│   ├── router/             # 路由配置
│   ├── store/              # Pinia 状态管理
│   ├── utils/              # 工具函数
│   └── views/              # 页面视图
├── vite/                   # Vite 插件定义
├── package.json            # 依赖与脚本
├── vite.config.js          # Vite 配置
└── README.md              # 本文件
```

## 核心模块详解

### 1. 应用入口（main.js）
初始化 Vue 应用：
- 创建 Vue 应用实例
- 注册全局插件（Element Plus、Router、Pinia、指令）
- 挂载全局方法与组件
- 引入权限守卫（permission.js）

### 2. 权限守卫（permission.js）
路由导航拦截与权限检查：

**核心流程**
1. 检查用户登录状态（`getToken()`）
2. 已登录用户：
   - 加载用户信息（`getInfo()`）
   - 生成动态路由（`generateRoutes()`）
   - 动态添加路由（`router.addRoute()`）
3. 未登录用户：重定向到 `/login`
4. 白名单路由（`/login`、`/register`）无需检查

### 3. 路由配置（router/index.js）

**常量路由** — 无需权限检查
- `/login`、`/register`：登录注册页
- `/`：首页（Dashboard）
- `/error/404`、`/401`：错误页
- `/redirect`：重定向页面

**动态路由** — 根据后端菜单与权限动态加载
- 从 `getRouters()` 获取菜单树
- 前端过滤并转换为 Vue Router 格式
- 动态添加到路由表

**路由元数据（meta）**
```javascript
{
  title: '页面名称',        // 侧边栏与面包屑显示
  icon: 'svg-icon-name',     // 菜单图标
  alwaysShow: false,         // 是否始终显示菜单
  noCache: false,           // 是否缓存页面
  breadcrumb: true,         // 是否显示面包屑
  activeMenu: '/system/user' // 高亮的菜单
}
```

### 4. 状态管理（store/）

使用 **Pinia**（Vue 3 官方推荐的轻量级状态管理库）

**store/modules/user.js** — 用户信息
- 状态：`token`、`id`、`name`、`nickName`、`avatar`、`roles`、`permissions`
- 操作：`login()`、`getInfo()`、`logOut()`

**store/modules/permission.js** — 路由权限
- 状态：`routes`、`addRoutes`、`sidebarRouters`
- 操作：`generateRoutes()`、`filterAsyncRouter()`

**store/modules/app.js** — 应用全局状态
- 侧边栏展开/收缩、主题、语言等

**store/modules/dict.js** — 字典缓存
- 缓存系统字典数据，避免重复请求

**store/modules/tagsView.js** — 标签页
- 管理已打开的页面标签

### 5. HTTP 请求（utils/request.js）

**Axios 实例配置**
- `baseURL`：从环境变量 `VITE_APP_BASE_API` 读取
- 超时：10 秒

**请求拦截**
- 自动在 `Authorization` 头中添加 JWT token
- GET 参数序列化与 URL 构建
- 防重复提交：1 秒内同一请求只允许一次

**响应拦截**
- 检查响应状态码 `code`
- 按错误码映射显示错误信息
- Token 过期自动调用刷新接口
- 二进制数据（如下载）直接返回

**导出功能**
```javascript
download(url, filename)  // 文件下载
blobValidate(blob)       // 验证下载内容
```

### 6. API 接口（api/）

按模块定义后端接口调用：

**api/login.js** — 认证
```javascript
login(username, password, code, uuid)    // 登录
logout(token)                             // 登出
getInfo()                                // 获取用户信息
getCodeImg()                             // 获取验证码
```

**api/menu.js** — 菜单
```javascript
getRouters()  // 获取菜单树（用于生成动态路由）
```

**api/system/** — 系统模块
- `user.js`：用户 CRUD、头像上传、权限管理
- `role.js`：角色 CRUD、权限分配
- `menu.js`：菜单 CRUD、树形选择
- `dept.js`：部门 CRUD、树形选择
- `dict.js`：字典管理、字典数据查询
- `config.js`：参数配置 CRUD

**api/monitor/** — 监控模块
- 日志、性能监控等

### 7. 页面视图（views/）

按业务功能模块组织：

```
views/
├── index.vue              # 首页（Dashboard）
├── login.vue              # 登录页
├── register.vue           # 注册页
├── error/                 # 错误页（404、401）
├── system/               # 系统管理
│   ├── user/             # 用户管理
│   ├── role/             # 角色管理
│   ├── menu/             # 菜单管理
│   ├── dept/             # 部门管理
│   ├── dict/             # 字典管理
│   └── config/           # 参数配置
├── monitor/              # 监控模块
└── tool/                 # 工具模块
```

### 8. 布局组件（layout/）

主布局框架结构：
- `layout/index.vue`：主布局框架
- `layout/components/`：
  - `Sidebar`：左侧菜单导航
  - `Navbar`：顶部导航栏
  - `TagsView`：标签页栏
  - `AppMain`：内容主区域

### 9. 工具函数（utils/）

**utils/auth.js** — Token 管理
```javascript
getToken()      // 从 localStorage 获取 token
setToken(token) // 存储 token
removeToken()   // 清除 token
```

**utils/request.js** — HTTP 请求
- Axios 实例与拦截器

**utils/dict.js** — 字典工具
```javascript
useDict(...dicts)      // 获取字典数据
getDicts(dictType)     // 按类型获取字典
```

**utils/validate.js** — 验证工具
```javascript
isEmail(email)     // 邮箱验证
isPhone(phone)     // 手机号验证
isHttp(path)      // 是否外链
isEmpty(value)    // 是否为空
```

**utils/permission.js** — 权限检查
```javascript
hasPermi(perms)   // 检查权限
hasRole(roles)    // 检查角色
```

**utils/ruoyi.js** — RuoYi 工具集
```javascript
parseTime(time)              // 时间格式化
addDateRange(params, range)  // 添加日期范围
handleTree(data)             // 数组转树形
selectDictLabel(dicts, value) // 字典值转标签
tansParams(params)           // 对象转 URL 参数
```

### 10. 指令与插件

**directive/permission/** — 权限指令
```vue
<!-- 检查权限 -->
<el-button v-haspermi="['system:user:add']">新增</el-button>

<!-- 检查角色 -->
<div v-hasrole="['admin']">管理员区域</div>
```

**plugins/** — 插件系统
- `auth.js`：权限检查插件
- `cache.js`：缓存插件（localStorage/sessionStorage）
- `download.js`：文件下载插件
- `modal.js`：模态框插件（确认、提示）
- `tab.js`：标签页管理插件

### 11. 构建配置（vite.config.js）

**主要配置项**
- `base`：应用基础路径（从 `VITE_APP_BASE_URL` 读取）
- `plugins`：Vite 插件（SVG 图标、压缩等）
- `resolve.alias`：路径别名（`@` = `src`）
- `build`：构建输出配置
- `server.proxy`：开发服务器代理

**开发服务器代理**
```javascript
proxy: {
  '/dev-api': {
    target: 'http://localhost:8000',
    rewrite: (p) => p.replace('/dev-api', '/api')
  }
}
```

## 核心功能流程

### 认证流程
1. 用户在登录页输入用户名、密码、验证码
2. 前端调用 `POST /api/login` 接口
3. 后端验证并返回 `access_token` 和 `refresh_token`
4. 前端使用 `setToken()` 存储到 localStorage
5. 后续请求在 `Authorization: Bearer {token}` 头中自动携带
6. Token 过期时自动调用刷新接口获取新 token

### 权限控制
1. 用户登录后调用 `getInfo()` 获取用户角色和权限
2. 调用 `getRouters()` 获取菜单树
3. 前端按权限过滤菜单
4. 动态添加路由到 Router
5. 使用指令 `v-haspermi` 和 `v-hasrole` 控制按钮显示

### 菜单与路由
```
后端 Menu 数据 → 树形菜单结构 → 前端动态路由
```
- 后端返回菜单树（含 `path`、`component`、`children` 等）
- 前端将字符串路径转换为 Vue 组件
- 动态添加到 Vue Router

## 常见开发任务

### 1. 添加新页面
1. 在 `views/` 下创建对应模块文件夹
2. 创建 `index.vue`（列表页）、`form.vue`（编辑页）等
3. 在后端定义 Menu 记录
4. 初始化后自动加载到前端菜单

### 2. 使用权限指令
```vue
<!-- 按钮权限 -->
<el-button v-haspermi="['system:user:add']" @click="handleAdd">新增</el-button>

<!-- 角色权限 -->
<div v-hasrole="['admin']">
  仅管理员可见的内容
</div>
```

### 3. 字典使用
```vue
<script setup>
import { useDict } from '@/utils/dict'

const { sys_user_sex } = useDict('sys_user_sex')  // 获取性别字典
</script>

<template>
  <!-- 显示字典标签 -->
  <dict-tag :options="sys_user_sex" :value="row.sex" />
</template>
```

### 4. API 调用
```javascript
import { getUserList, addUser } from '@/api/system/user'

// 获取列表
const data = await getUserList({ pageNum: 1, pageSize: 10 })

// 新增
await addUser({ username: 'admin', nickName: '管理员' })
```

### 5. 全局组件使用
```vue
<!-- 分页 -->
<pagination :total="total" :page="page" :limit="limit" @pagination="handleQuery" />

<!-- 富文本编辑 -->
<editor v-model="content" />

<!-- 文件上传 -->
<file-upload @success="handleUpload" />
```

## 部署指南

### 生产构建
```bash
npm run build:prod
```

输出到 `dist/` 目录：
- `index.html`：主入口
- `static/js/`：JavaScript 文件（分割代码）
- `static/css/`：样式文件
- `static/img/`：图像资源

### 部署方式

**方式 1：Django 后端静态托管**
```bash
# 将构建产物复制到后端
cp -r dist/* ../backend/dist/
```
Django 会自动提供：http://localhost:8000/

**方式 2：Nginx 独立部署**
```nginx
server {
  listen 80;
  root /path/to/dist;
  
  location / {
    try_files $uri $uri/ /index.html;  # SPA 路由处理
  }
  
  location /api/ {
    proxy_pass http://backend:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

## 环境变量

### .env.development（开发环境）
```env
VITE_APP_ENV = development
VITE_APP_BASE_URL = /
VITE_APP_BASE_API = /dev-api
```

### .env.production（生产环境）
```env
VITE_APP_ENV = production
VITE_APP_BASE_URL = /
VITE_APP_BASE_API = /api
```

修改后端 API 地址后，重新构建即可。

## 常见问题

### Q: 如何修改开发服务器端口？
A: 编辑 `vite.config.js`，修改 `server.port`

```javascript
server: {
  port: 8080,  // 改为其他端口
  // ...
}
```

### Q: 如何添加全局组件？
A: 在 `main.js` 中注册：

```javascript
import MyComponent from '@/components/MyComponent'
app.component('MyComponent', MyComponent)
```

### Q: 如何修改主题色？
A: 编辑 `assets/styles/index.scss` 中的 CSS 变量或使用 Element Plus 主题定制

### Q: 前端如何判断用户权限？
A: 使用以下方法之一：
```javascript
// 方法 1：使用 Pinia Store
const userStore = useUserStore()
if (userStore.permissions.includes('system:user:add')) {
  // 用户有权限
}

// 方法 2：使用指令
// 在模板中用 v-haspermi 指令
```

### Q: 如何实现自动登出？
A: 修改 `utils/request.js` 的响应拦截器，当收到 401 状态码时触发登出

```javascript
if (code === 401) {
  useUserStore().logOut()
}
```

## 相关文件链接
- [main.js](src/main.js) — 应用入口
- [permission.js](src/permission.js) — 权限守卫
- [router/index.js](src/router/index.js) — 路由配置
- [utils/request.js](src/utils/request.js) — HTTP 请求
- [store/modules/user.js](src/store/modules/user.js) — 用户状态
- [store/modules/permission.js](src/store/modules/permission.js) — 权限与路由
- [vite.config.js](vite.config.js) — Vite 构建配置
