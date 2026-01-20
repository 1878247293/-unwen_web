# 科研论文整理与总结网站 - 前端

基于 React + Vite + Ant Design 的前端应用

## 技术栈

- **框架**: React 18.2+
- **构建工具**: Vite 5.0+
- **UI组件库**: Ant Design 5.12+
- **路由**: React Router 6.20+
- **状态管理**: Zustand 4.4+
- **HTTP客户端**: Axios 1.6+
- **Markdown**: React Markdown 9.0+

## 项目结构

```
frontend/
├── src/
│   ├── assets/         # 静态资源
│   │   ├── images/     # 图片
│   │   └── styles/     # 全局样式
│   ├── components/     # 通用组件
│   │   └── Layout.jsx  # 布局组件
│   ├── pages/          # 页面组件
│   │   ├── Login.jsx   # 登录页
│   │   ├── Register.jsx # 注册页
│   │   ├── Dashboard.jsx # 仪表盘
│   │   └── Papers.jsx  # 论文库
│   ├── services/       # API服务
│   │   ├── request.js  # Axios封装
│   │   └── authService.js # 认证服务
│   ├── store/          # 状态管理
│   │   └── authStore.js # 认证状态
│   ├── utils/          # 工具函数
│   ├── App.jsx         # 根组件
│   └── main.jsx        # 入口文件
├── public/             # 公共资源
├── index.html          # HTML模板
├── vite.config.js      # Vite配置
└── package.json        # 依赖配置
```

## 快速开始

### 方式一：使用一键启动脚本（推荐）⭐

**Linux/Mac:**
```bash
bash start.sh
```

脚本会自动：
- 检查 Node.js 环境
- 自动使用淘宝镜像加速下载
- 安装所有依赖（首次运行）
- 启动开发服务器

### 方式二：使用配置脚本

```bash
# 第一步：安装依赖
bash setup.sh

# 第二步：启动服务
npm run dev
```

### 方式三：手动安装

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动

> 💡 **提示**: 推荐使用一键启动脚本 `bash start.sh`，最简单快捷！

### 3. 构建生产版本

```bash
npm run build
```

构建输出将在 `dist/` 目录

---

## 🚀 启动脚本

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `start.sh` ⭐ | 一键启动 | 首次启动、日常开发 |
| `setup.sh` | 配置环境 | 仅安装依赖 |
| `clean.sh` | 清理重装 | 依赖有问题时 |

详细说明请查看 [脚本使用说明.md](脚本使用说明.md)

## 功能模块

### 已实现

- ✅ 用户注册
- ✅ 用户登录
- ✅ 用户认证（JWT）
- ✅ 路由守卫
- ✅ 基础布局
- ✅ 仪表盘（框架）
- ✅ 论文库（框架）

### 待实现

- [ ] 论文CRUD功能
- [ ] 笔记编辑器
- [ ] 标签管理
- [ ] AI助手集成
- [ ] 个人中心
- [ ] 管理员功能

## API代理配置

开发环境下，Vite自动代理API请求到后端：

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/uploads': 'http://localhost:8000',
  }
}
```

## 状态管理

使用Zustand进行状态管理，支持持久化：

```javascript
import { useAuthStore } from '@/store/authStore'

// 在组件中使用
const { user, login, logout } = useAuthStore()
```

## 路由配置

```
/login          - 登录页（公开）
/register       - 注册页（公开）
/               - 仪表盘（需登录）
/papers         - 论文库（需登录）
```

## 开发规范

### 组件命名

- 使用PascalCase命名组件文件：`MyComponent.jsx`
- 组件内部使用函数式组件

### 样式文件

- 每个组件可以有对应的CSS文件：`MyComponent.css`
- 全局样式放在 `assets/styles/` 目录

### API调用

统一使用services中的服务函数：

```javascript
import { authService } from '@/services/authService'

const handleLogin = async (values) => {
  const response = await authService.login(values)
  // ...
}
```

## 浏览器支持

- Chrome (推荐)
- Firefox
- Edge
- Safari

## 常见问题

### 如何添加新页面？

1. 在 `src/pages/` 创建页面组件
2. 在 `App.jsx` 中添加路由
3. 在布局菜单中添加导航（如需要）

### 如何添加新的API接口？

1. 在 `src/services/` 创建或扩展service文件
2. 使用 `request` 实例进行HTTP调用

## 下一步

- [ ] 实现论文管理完整功能
- [ ] 集成Markdown编辑器
- [ ] 添加AI助手浮动窗口
- [ ] 优化UI/UX
- [ ] 添加单元测试

## 许可证

MIT License
