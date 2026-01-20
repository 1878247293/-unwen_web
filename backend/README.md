# 科研论文整理与总结网站 - 后端

基于 FastAPI + SQLite 的后端服务

## 技术栈

- **框架**: FastAPI 0.104+
- **数据库**: SQLite (异步)
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT (python-jose)
- **密码加密**: Passlib + Bcrypt

## 项目结构

```
backend/
├── app/
│   ├── models/          # 数据模型
│   ├── routes/          # API路由
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # 业务逻辑
│   ├── utils/           # 工具函数
│   ├── config.py        # 配置管理
│   └── main.py          # 应用入口
├── data/                # 数据目录
│   ├── database.db      # SQLite数据库
│   └── uploads/         # 上传文件
├── scripts/             # 脚本
│   └── init_db.py       # 数据库初始化
├── requirements.txt     # 依赖包
└── .env                 # 环境变量
```

## 快速开始

### 1. 安装依赖

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置（已自动完成）

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

这将创建数据库表并创建默认管理员账号：
- 用户名: `admin`
- 密码: `admin123`

**重要**: 首次登录后请立即修改密码！

### 4. 启动服务

```bash
# 开发模式（自动重载）
python app/main.py

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 认证相关

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出

### 用户相关

- `GET /api/users/me` - 获取当前用户信息
- `PUT /api/users/me` - 更新当前用户信息
- `PUT /api/users/me/password` - 修改密码
- `GET /api/users/` - 获取所有用户（管理员）
- `PUT /api/users/{user_id}/status` - 更新用户状态（管理员）

## 数据库表结构

### 核心表

1. **users** - 用户表
2. **papers** - 论文表
3. **notes** - 笔记表
4. **tags** - 标签表
5. **paper_tags** - 论文-标签关联表
6. **ai_conversations** - AI对话会话表
7. **ai_messages** - AI对话消息表
8. **user_ai_quotas** - 用户AI额度表
9. **audit_logs** - 操作日志表

## 开发说明

### 添加新功能

1. 在 `models/database.py` 中定义数据模型
2. 在 `schemas/` 中创建 Pydantic schema
3. 在 `services/` 中实现业务逻辑
4. 在 `routes/` 中创建 API 路由
5. 在 `main.py` 中注册路由

### 权限控制

使用依赖注入进行权限验证：

```python
from app.utils.dependencies import get_current_user, get_current_admin_user

# 需要登录
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    pass

# 需要管理员权限
@router.get("/admin")
async def admin_route(current_user: User = Depends(get_current_admin_user)):
    pass
```

## 部署

### 生产环境配置

1. 修改 `.env` 中的 `SECRET_KEY`
2. 设置 `DEBUG=False`
3. 配置生产数据库（可选）
4. 使用 gunicorn + uvicorn 部署

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 常见问题

### 数据库文件在哪里？

SQLite 数据库文件位于 `data/database.db`

### 如何重置数据库？

```bash
# 删除数据库文件
rm data/database.db

# 重新初始化
python scripts/init_db.py
```

### 如何备份数据？

```bash
# 复制整个 data 目录即可
cp -r data data_backup_$(date +%Y%m%d)
```

## 下一步

- [ ] 实现论文管理API
- [ ] 实现笔记管理API
- [ ] 实现标签管理API
- [ ] 集成AI助手功能
- [ ] 添加单元测试

## 许可证

MIT License
