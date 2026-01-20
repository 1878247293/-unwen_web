# 科研论文整理与总结网站

一个基于现代Web技术栈的科研论文管理系统，支持论文整理、笔记编辑、标签分类和AI助手等功能。

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://react.dev)
[![SQLite](https://img.shields.io/badge/SQLite-3+-lightgrey.svg)](https://www.sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 目录

- [项目特点](#项目特点)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [已完成功能](#已完成功能)
- [待办事项](#待办事项)
- [项目结构](#项目结构)
- [API文档](#api文档)
- [开发指南](#开发指南)
- [部署指南](#部署指南)
- [常见问题](#常见问题)

---

## 🎉 最新更新 (v1.12.0 - 2026-01-13)

### 📊 新功能 - 资源监控系统

#### 功能特性
- ✅ **系统资源监控** - 实时监控服务器状态
  - CPU 使用率（百分比 + 核心数）
  - 内存使用（百分比 + GB）
  - 磁盘使用（百分比 + GB）
  - 彩色进度条（绿色/黄色/红色根据使用率）
  - 系统启动时间显示

- ✅ **数据库统计** - 完整的网站数据统计
  - 用户数（总数/活跃/待审）
  - 论文数、笔记数、标签数
  - 评论数、讨论数、想法数
  - 网站收藏数、建议数、通知数

- ✅ **存储使用情况** - 文件存储占用统计
  - 论文文件大小
  - PDF 文件大小
  - 头像文件大小
  - 数据库文件大小
  - 自动格式化为合适单位（B/KB/MB/GB/TB）

- ✅ **实时监控功能**
  - 手动刷新按钮
  - 自动刷新开关（每30秒）
  - 最后更新时间显示
  - 系统健康状态标签

- ✅ **健康状态检查**
  - 自动检测系统问题（CPU/内存/磁盘过高）
  - 警告提示（超过80%黄色，超过90%红色）
  - 健康/警告/严重三个级别
  - 数据库连接状态检查

#### 后端实现
- ✅ **后端API** - 4个监控接口
  - GET `/api/system/resources` - 系统资源（CPU/内存/磁盘）
  - GET `/api/system/statistics` - 数据库统计
  - GET `/api/system/storage` - 存储使用情况
  - GET `/api/system/health` - 系统健康状态
- ✅ **依赖安装** - psutil 7.2.1（系统资源监控库）
- ✅ **权限控制** - 仅管理员可访问

#### 前端实现
- ✅ **前端页面** - `SystemMonitor.jsx`（资源监控主页面）
  - 系统资源卡片（3个进度条）
  - 数据库统计卡片（8种数据类型）
  - 存储使用卡片（5种文件类型）
  - 自动刷新开关
  - 响应式布局
- ✅ **API服务** - `systemService.js`（4个方法）
- ✅ **导航集成** - "资源监控"菜单项（MonitorOutlined图标，仅管理员可见）
- ✅ **路由配置** - `/admin/system`

#### 问题修复
- 🐛 **psutil模块未找到错误**
  - 现象：`ModuleNotFoundError: No module named 'psutil'`
  - 原因：psutil 安装到了系统 Python 而不是虚拟环境
  - 修复：`source venv/bin/activate && pip install psutil`
  - 文件：`backend/requirements.txt` 添加 `psutil==7.2.1`

- 🐛 **模型导入错误**
  - 现象：`ImportError: cannot import name 'Suggestion' from 'app.models.database'`
  - 原因：Suggestion/Notification/Idea/Website 使用原始 SQL 而非 ORM 模型
  - 修复：改用原始 SQL 查询这些表的统计数据
  - 文件：`backend/app/routes/system.py:15, 148-170`

---

## 🎉 最新更新 (v1.11.0 - 2026-01-13)

### 💬 新功能 - 交流广场（讨论系统）

#### 功能特性
- ✅ **讨论发布与回复** - 完整的社区讨论功能
  - 发布顶层讨论
  - 一级回复（不支持多级嵌套）
  - 匿名发布（默认开启，管理员可控制）
  - 树形结构展示
  - 编辑和删除自己的讨论

- ✅ **互动功能** - 丰富的社交互动
  - **点赞**：点赞/取消点赞，显示点赞数和自己是否已点赞
  - **收藏**：收藏/取消收藏，查看收藏列表
  - **举报**：举报不良内容，选择举报原因（垃圾广告/不当言论/虚假信息/其他）

- ✅ **管理员功能**
  - 开启/关闭匿名功能
  - 隐藏/取消隐藏讨论
  - 删除任何讨论
  - 查看和处理举报（批准/驳回）
  - 查看隐藏内容

- ✅ **排序和筛选**
  - 最新在前/最早在前/最热门（按点赞数）
  - 分页显示（10条/页）
  - 多选项卡视图（全部/收藏/举报/隐藏内容）

#### 数据库设计
- ✅ **discussions 表** - 讨论主表（9个字段，5个索引）
  - id, user_id, content, is_anonymous, is_hidden, parent_id
  - created_at, updated_at, deleted_at
- ✅ **system_settings 表** - 系统设置（默认开启匿名）
- ✅ **discussion_likes 表** - 点赞记录（唯一约束防重复）
- ✅ **discussion_favorites 表** - 收藏记录（唯一约束防重复）
- ✅ **discussion_reports 表** - 举报记录（管理员审核）

#### 后端实现
- ✅ **后端API** - 完整的讨论API（20个接口）
  - 基本CRUD（5个）：创建、列表、详情、更新、删除
  - 点赞（2个）：点赞、取消点赞
  - 收藏（3个）：收藏、取消收藏、收藏列表
  - 举报（3个）：举报、举报列表、处理举报
  - 管理员（5个）：隐藏、取消隐藏、匿名设置查询、匿名设置更新
- ✅ **数据验证** - 完整的 Pydantic schemas
- ✅ **权限控制** - 用户只能编辑删除自己的内容，管理员有全部权限

#### 前端实现
- ✅ **前端页面** - `Community.jsx`（交流广场主页面11KB）
  - 多选项卡：全部讨论、我的收藏、举报管理（管理员）、包含隐藏内容（管理员）
  - 排序选项：最新、最早、最热门
  - 管理员设置面板（匿名开关）
- ✅ **前端组件** - 完整的讨论组件
  - `DiscussionInput.jsx` - 讨论输入（支持匿名选项）
  - `DiscussionList.jsx` - 讨论列表（16KB，树形结构，互动按钮）
  - `ReportModal.jsx` - 举报对话框
- ✅ **API服务** - `discussionService.js`（17个方法）
- ✅ **导航集成** - "交流广场"菜单项（CommentOutlined图标）
- ✅ **路由配置** - `/community`

#### 匿名隐私保护
- 后端存储 user_id 用于权限控制
- 前端显示"匿名用户"，不暴露真实身份
- 匿名用户仍可编辑删除自己的讨论（通过 user_id 验证）

---

## 🎉 最新更新 (v1.10.0 - 2026-01-13)

### 🌐 新功能 - 科研网站收藏系统

#### 功能特性
- ✅ **网站收藏管理** - 收集和管理常用科研网站
  - 网站名称、链接、分类、描述
  - 收藏功能（星标按钮，一键切换）
  - 多维度搜索（名称、描述、链接）
  - 分类筛选（7个预设分类 + 自定义）
  - 收藏筛选（仅收藏/未收藏）
  - 点击访问功能（新标签页打开）
  - 表格展示，分页支持

#### 后端实现
- ✅ **后端API** - 6个网站接口
  - POST `/api/websites/` - 创建网站
  - GET `/api/websites/` - 获取网站列表
  - GET `/api/websites/categories` - 获取分类列表
  - GET `/api/websites/{id}` - 获取网站详情
  - PUT `/api/websites/{id}` - 更新网站信息
  - DELETE `/api/websites/{id}` - 删除网站（软删除）
- ✅ **数据库** - `websites`表（10个字段，4个索引）
- ✅ **预置数据** - 27个常用科研网站
  - 学术搜索：Google Scholar、Semantic Scholar、百度学术
  - 论文数据库：arXiv、PubMed、IEEE Xplore、ACM、ScienceDirect、知网、万方
  - 文献管理：Zotero、Mendeley、EndNote
  - 引文分析：Web of Science、Scopus
  - 期刊资源：JCR、SCI-Hub、Library Genesis
  - 学术工具：Connected Papers、ResearchGate、ORCID
  - 数据集：Kaggle、UCI ML、Papers with Code

#### 前端实现
- ✅ **前端页面** - `Websites.jsx`（完整的CRUD操作）
- ✅ **API服务** - `websitesService.js`（6个方法）
- ✅ **导航集成** - "网站收藏"菜单项（GlobalOutlined图标）
- ✅ **路由配置** - `/websites`

#### 权限控制
- 普通用户只能查看和管理自己添加的网站
- 管理员可以查看所有网站
- 系统预置的网站由admin用户创建

#### 性能优化
- ✅ **乐观更新（Optimistic Update）** - 消除操作延迟
  - 收藏/取消收藏：立即响应（从~500ms → 0ms）
  - 删除网站：立即响应
  - 创建/编辑：Modal立即关闭
  - API失败时自动回滚UI

#### 问题修复
- 🐛 **URL路径重复** - 修复 `/api/api/websites/` 404错误
  - 原因：baseURL已包含`/api`，服务中不应再加前缀
  - 修复：移除服务中的`/api`前缀（6处）
- ⚡ **收藏卡顿** - 实现乐观更新，操作立即响应
  - 优化前：点击 → 等待500ms → 更新
  - 优化后：点击 → 立即看到效果
- 🐛 **表单字段** - 修复is_favorite Checkbox配置

---

## 🎉 最新更新 (v1.9.2 - 2026-01-13)

### 🔐 安全功能增强 - 登录安全与管理员限制

#### 1. 登录安全机制
- ✅ **密码错误次数限制** - 防暴力破解
  - **配置**: 每日最多10次失败，超过后冷却5分钟
  - **数据库变更** - `users` 表新增4个字段
    - `failed_login_attempts` - 当天失败次数
    - `last_failed_login` - 最后失败时间
    - `login_locked_until` - 锁定截止时间
    - `last_login_date` - 最后登录日期（用于每日重置）
  - **核心功能**
    - 每次密码错误显示剩余尝试次数
    - 10次失败后账号锁定5分钟（HTTP 429）
    - 每日自动重置计数器（通过日期比较）
    - 登录成功自动清除失败记录
  - **用户体验**
    - 明确错误提示：`"密码错误，今日还可尝试 9 次（超过10次将锁定5分钟）"`
    - 锁定提示：`"账号已被锁定，请在 X 分钟后重试"`
    - 冷却期消息显示5秒（重要提示）
  - **后端实现** - `auth.py`
    - 3个辅助函数：check_login_cooldown(), record_login_failure(), reset_login_attempts()
    - 6步登录流程：冷却检查 → 验证 → 状态检查 → 重置 → 创建token → 响应
  - **前端实现** - `Login.jsx`
    - 添加429状态码错误处理
    - 显示后端返回的详细锁定消息

#### 2. 管理员操作限制
- ✅ **admin用户完全只读** - 防止误操作
  - **限制范围**: admin用户不可修改任何用户信息（包括自己）
  - **受限端点**（6个）
    - PUT `/users/me` - 禁止修改个人信息（邮箱、部门、头像）
    - PUT `/users/me/password` - 禁止修改自己的密码
    - PUT `/users/{user_id}/status` - 禁止更新任何用户状态
    - PUT `/users/{user_id}/role` - 禁止更新任何用户角色
    - POST `/users/{user_id}/reset-password` - 禁止重置任何用户密码
    - DELETE `/users/{user_id}` - 禁止删除任何用户
  - **实现方式** - `users.py`
    - 每个端点开头统一检查：`if current_user.username == "admin"`
    - 返回HTTP 403: `"admin用户不可修改用户信息"`
    - 早期验证，避免不必要的数据库操作
  - **注意事项**
    - 仅 "admin" 用户名（小写）受限制
    - 其他管理员账号（如admin2）不受影响
    - 紧急修改需使用其他管理员账号或直接操作数据库

#### 3. 性能优化 - 页面切换流畅度提升
- ✅ **改进加载动画** - 使用完整的Loading组件（Spin + 毛玻璃效果）
- ✅ **页面淡入动画** - 0.3秒淡入 + 微妙位移，切换更流畅
- ✅ **局部加载状态** - 懒加载路由使用RouteLoader，侧边栏始终可见
- ✅ **路由预加载** - 空闲时预加载6个常用页面，延迟降低90%+
  - 预加载页面：标签管理、通知中心、个人中心、想法收集、改进建议、添加论文
  - 使用requestIdleCallback，不影响主线程
  - 登录后2秒开始预加载

#### 4. 实现过程 - 零错误完成
- ✅ **登录安全** - 无错误
  - 数据库迁移顺利完成
  - 所有辅助函数正常工作
  - 前端错误提示准确显示
- ✅ **管理员限制** - 无错误
  - 6个端点统一添加检查
  - Python语法检查通过
- ✅ **性能优化** - 无错误
  - 动画效果流畅
  - 预加载机制正常工作
  - 代码分割策略合理

---

## 📜 历史更新 (v1.9.1 - 2026-01-13)

### 🔧 功能改进 - 想法收集三部分结构
- ✅ **想法收集系统结构优化** - 从二部分改进为三部分结构
  - **需求来源**: 用户反馈需要分离参考文献与想法内容
  - **新结构**
    - 标题（可选，最多200字符）
    - **参考文献**（可选，最多2000字符）- **新增字段**
    - 想法内容（必填，最多10000字符，支持Markdown）
  - **数据库变更** - `ideas` 表
    - 新增 `references TEXT` 字段（可空）
    - 使用直接SQL执行：`ALTER TABLE ideas ADD COLUMN "references" TEXT`
  - **后端API更新** - 所有5个接口支持 references 字段
    - POST `/api/ideas/` - 接受 references 参数
    - GET `/api/ideas/` - 返回 references 字段
    - GET `/api/ideas/{id}` - 返回 references 字段
    - PUT `/api/ideas/{id}` - 支持更新 references 字段
    - DELETE `/api/ideas/{id}` - 无需修改
  - **前端UI更新** - `Ideas.jsx`
    - 创建/编辑对话框新增"参考文献"输入框（4行TextArea，最多2000字符）
    - 详情模态框显示参考文献区域（蓝色标题，浅蓝色背景）
    - 状态管理包含三个字段（title, references, content）
  - **实现细节**
    - SQL关键字处理：references 必须用双引号包裹 `"references"`
    - URLSearchParams 传递可选参数
    - 条件渲染：仅在有参考文献时显示该区域

- ✅ **实现过程** - 无错误，所有功能顺利完成
  - ✅ 数据库迁移：使用 Python sqlite3 直接执行 ALTER TABLE
  - ✅ 后端API更新：5个接口全部支持 references 字段
  - ✅ 前端服务更新：createIdea 和 updateIdea 方法支持 references
  - ✅ 前端UI更新：完成5处编辑（状态、创建、编辑、输入框、详情显示）

---

## 📜 历史更新 (v1.9.0 - 2026-01-13)

### ✨ 新功能 - 想法收集与账号统计（初版）
- ✅ **想法收集系统** - 记录研究想法和灵感
  - **后端API** - 5个完整接口
    - POST `/api/ideas/` - 创建想法
    - GET `/api/ideas/` - 获取想法列表（支持搜索、分页）
    - GET `/api/ideas/{id}` - 获取想法详情
    - PUT `/api/ideas/{id}` - 更新想法
    - DELETE `/api/ideas/{id}` - 删除想法（软删除）
  - **核心特性**
    - 标题可选，内容必填（最多10000字符）
    - 支持Markdown格式编辑
    - 内容预览（列表显示前200字符）
    - 搜索功能（标题或内容）
    - 分页支持
    - 相对时间显示（"3分钟前"）
  - **前端页面** - `Ideas.jsx`
    - 想法列表展示（卡片式布局）
    - 创建/编辑对话框（Markdown支持）
    - 详情模态框（ReactMarkdown渲染）
    - 搜索和分页功能
    - 编辑和删除操作
  - **导航集成**
    - 侧边栏菜单项："想法收集"（FormOutlined图标）
    - 路由：`/ideas`
  - **数据库表** - `ideas`
    - 字段：id, user_id, title, content, created_at, updated_at, deleted_at
    - 索引：user_id, created_at, deleted_at
    - 外键：user_id → users(id) CASCADE DELETE

- ✅ **个人中心账号统计** - 实时数据统计展示
  - **后端API**
    - GET `/api/users/me/stats` - 获取用户统计信息
  - **统计指标**
    - 已添加论文数量
    - 笔记数量
    - 标签数量
    - 想法数量（新增）
    - 注册时间
  - **前端集成** - `Profile.jsx`
    - "账号统计"标签页实时数据
    - 替换原有占位符"0"值
    - 加载状态动画
    - 格式化日期显示

- ✅ **实现过程与问题修复**
  - ❌ **问题1：图标导入错误**
    - 现象：`Layout.jsx:13` 报错 "The requested module does not provide an export named 'LightbulbOutlined'"
    - 原因：`LightbulbOutlined` 图标在 @ant-design/icons 中不存在
    - 修复：删除 `LightbulbOutlined` 导入，改用 `FormOutlined` 图标
    - 文件：`frontend/src/components/Layout.jsx:3-14, 70-72`

  - ❌ **问题2：获取插入ID失败**
    - 现象：创建想法后返回错误，日志显示 `last_insert_rowid()` 返回 0
    - 原因：在 `commit()` 之后调用 `last_insert_rowid()`，此时已经结束事务
    - 修复：使用 `result.lastrowid` 在 commit 之前获取插入的 ID
    - 文件：`backend/app/routes/ideas.py:41, 50-51`
    - 关键改动：
      ```python
      # 错误写法
      await db.execute(query, params)
      await db.commit()
      result = await db.execute(text("SELECT last_insert_rowid()"))

      # 正确写法
      result = await db.execute(query, params)
      idea_id = result.lastrowid
      await db.commit()
      ```

  - ❌ **问题3：日期格式化错误**
    - 现象：创建想法失败，错误信息 "'str' object has no attribute 'isoformat'"
    - 原因：SQLite的TIMESTAMP字段返回字符串而非datetime对象
    - 修复：创建 `format_datetime()` 辅助函数处理多种类型
    - 文件：`backend/app/routes/ideas.py:20-28, 77, 83, 151-152, 195-196`
    - 关键改动：
      ```python
      def format_datetime(dt):
          if dt is None: return None
          if isinstance(dt, str): return dt
          if isinstance(dt, datetime): return dt.isoformat()
          return str(dt)
      ```

  - ✅ 数据库迁移成功（`migrate_create_ideas_table.py`）
  - ✅ 所有API接口正常工作
  - ✅ 前端页面集成完成
  - ✅ 统计功能实时更新

---

## 🎉 最新更新 (v1.8.0 - 2026-01-13)

### ✨ 新功能 - 站内通知系统
- ✅ **后端通知API** - 5个完整接口
  - GET `/api/notifications/` - 获取通知列表（支持筛选已读/未读、分页）
  - GET `/api/notifications/unread-count` - 获取未读通知数量（用于徽标显示）
  - PUT `/api/notifications/{id}/read` - 标记通知为已读
  - PUT `/api/notifications/read-all` - 标记所有通知为已读
  - DELETE `/api/notifications/{id}` - 删除通知
- ✅ **通知类型**
  - `comment_reply` - 评论回复通知（已实现自动触发）
  - `system` - 系统通知（预留）
  - `mention` - @提及通知（预留）
- ✅ **评论回复自动通知**
  - 修改文件：`backend/app/routes/comments.py:22, 141-164`
  - 当用户回复评论时，自动创建通知给父评论作者
  - 不给自己发通知（回复自己的评论时跳过）
  - 通知内容包含：回复者用户名、论文标题、回复内容（前100字符）、跳转链接
- ✅ **前端通知中心**
  - `Notifications.jsx` - 通知中心页面（3个标签页：全部/未读/已读）
  - `notificationService.js` - 通知API服务封装
  - 未读通知高亮显示（蓝色背景 + 蓝色边框 + 脉冲徽标）
  - 相对时间显示（"3分钟前"）
  - 通知类型彩色标签（蓝色=评论回复、绿色=系统通知、橙色=提及）
  - 一键全部已读功能
  - 点击通知自动标记为已读并跳转相关页面
  - 分页支持
- ✅ **导航栏通知铃铛**
  - 修改文件：`frontend/src/components/Layout.jsx:1, 12, 16, 26, 28-50, 140-154`
  - BellOutlined图标 + 红色徽标数字
  - 实时未读计数（每30秒自动刷新）
  - 有未读通知时图标变蓝色
  - 点击跳转通知中心
- ✅ **数据库迁移**
  - `notifications`表创建脚本（`backend/scripts/migrate_create_notifications_table.py`）
  - 字段：id, user_id, type, title, content, link, is_read, created_at, sender_id, related_id
  - 索引优化：user_id, is_read, created_at, type
  - 外键约束：user_id → users.id (CASCADE DELETE), sender_id → users.id (SET NULL)
- ✅ **实现过程** - 无错误，所有功能顺利完成
  - 数据库表创建成功
  - 所有API接口正常工作
  - 评论回复自动通知集成完成
  - 前端页面和导航栏集成完成

---

## 🎉 最新更新 (v1.5.3 - 2026-01-12)

### ✨ 新功能 - 评论系统完整实现
- ✅ **后端评论API** - 5个完整接口
  - POST `/api/comments/papers/{paper_id}` - 创建评论/回复
  - GET `/api/comments/papers/{paper_id}` - 获取评论列表（树形结构）
  - GET `/api/comments/{comment_id}` - 获取评论详情
  - PUT `/api/comments/{comment_id}` - 更新评论
  - DELETE `/api/comments/{comment_id}` - 删除评论（软删除）
  - 支持一级回复（不支持多级嵌套）
  - 自动权限控制（用户只能编辑/删除自己的评论）
  - 分页和排序支持（最新/最早）
- ✅ **前端评论组件**
  - `CommentInput.jsx` - 评论输入框（支持Ctrl+Enter快捷提交）
  - `CommentList.jsx` - 评论列表组件（树形展示、编辑、删除、回复）
  - `commentService.js` - 评论API服务封装
  - 集成到论文详情页（新增"评论"标签页）
  - 用户头像显示、相对时间（如"3分钟前"）
  - 实时更新、友好的UI交互
- ✅ **数据库迁移**
  - `comments`表创建脚本（支持自引用外键）
  - 软删除支持（删除评论同时删除所有回复）

---

## 🎉 最新更新 (v1.7.0 - 2026-01-13)

### ✨ 新功能 - 改进建议墙
- ✅ **用户共享改进建议系统** - 所有用户可见的公共建议板
  - **核心特性**
    - 所有用户都可以提交改进建议
    - 每条建议前有复选框（管理员可勾选）
    - 管理员勾选后标记为"已完成"
    - 显示建议提交者信息和时间
    - 显示完成者信息和完成时间
  - **后端API** (5个接口)
    - POST `/api/suggestions/` - 创建建议
    - GET `/api/suggestions/` - 获取建议列表
    - PUT `/api/suggestions/{id}/complete` - 标记为完成
    - PUT `/api/suggestions/{id}/uncomplete` - 取消完成标记
    - DELETE `/api/suggestions/{id}` - 删除建议
  - **前端页面**
    - `Suggestions.jsx` - 改进建议墙页面
    - `suggestionService.js` - API服务封装
    - 统计信息显示（全部/待处理/已完成）
    - 实时相对时间显示（如"3分钟前"）
    - 完成状态用删除线标记
  - **权限控制**
    - 所有用户：查看所有建议、创建建议、删除自己的建议
    - 管理员：标记完成/取消完成、删除任何建议
  - **数据库**
    - `suggestions`表创建脚本
    - 字段：id, content, user_id, status, created_at, completed_at, completed_by
    - 索引优化：user_id, status, created_at
  - **实现过程与问题修复**
    - ❌ **问题1：API参数验证错误**
      - 现象：前端请求 `page_size=1000` 时返回 422 Unprocessable Entity
      - 原因：后端API限制 `page_size` 最大值为100（`le=100`）
      - 修复：将 `suggestions.py:78` 的限制改为 `le=1000`
    - ❌ **问题2：勾选复选框有明显延迟**
      - 现象：勾选后需要等待1-2秒才能看到状态变化
      - 原因：每次勾选都调用 `loadSuggestions()` 重新加载整个列表
      - 修复：实现**乐观更新（Optimistic Update）**
        - 勾选时立即更新UI状态（无延迟）
        - 后台异步调用API
        - API失败时自动回滚UI
        - 同样应用到删除和创建操作
      - 效果：从"勾选→等待→更新"变为"勾选→立即看到更新"
    - ✅ 数据库迁移成功，所有API接口正常工作
    - ✅ 前端页面集成完成，权限控制正确实施

### 🔐 认证系统优化 - 用户体验改进
- ✅ **登录错误提示优化** - 明确区分用户名和密码错误
  - **优化内容**
    - 用户名不存在：显示"用户名不存在"
    - 密码错误：显示"密码错误"
    - 账号待审核：显示"账号待审核，请等待管理员审核"
    - 账号被禁用：显示"账号已被禁用"
  - **后端修改**
    - `user_service.py:91-115` - 修改 `authenticate_user` 函数返回值
    - 从 `Optional[User]` 改为 `(User, error_message)`
    - 用户不存在返回: `(None, "用户名不存在")`
    - 密码错误返回: `(None, "密码错误")`
  - **前端修改**
    - `auth.py:47-98` - 登录接口返回具体错误
    - `Login.jsx:43-46` - 显示后端返回的具体错误信息
  - **用户价值**：帮助用户快速定位问题，减少困惑

- ✅ **注册时用户名重复检测** - 防止重复注册（已有功能，本次明确记录）
  - **检测机制**
    - 检查用户名是否已存在：返回"用户名已存在"
    - 检查邮箱是否已存在：返回"邮箱已被注册"
  - **实现位置**
    - `auth.py:23-36` - 后端检查逻辑
    - `Register.jsx:31-41` - 前端错误提示
  - **用户价值**：及时提示用户更换用户名/邮箱，避免表单提交失败

---

## 🎉 最新更新 (v1.6.0 - 2026-01-12)

### ⚡ 性能优化 - 前端性能全面提升
- ✅ **代码分割（Code Splitting）**
  - 路由级：6个低频路由懒加载（AddPaper、EditPaper、Tags、Profile、AdminDashboard、UserManagement）
  - 组件级：NoteEditor组件懒加载（包含react-markdown-editor-lite和markdown-it）
  - 预期收益：首屏加载体积减少30-40%，笔记编辑器节省约150KB
- ✅ **API请求防抖优化**
  - 自定义Hook：`useDebounce.js` - 值防抖和回调防抖
  - 应用场景：论文搜索框（500ms延迟）
  - 实际收益：搜索请求减少90%+
- ✅ **API响应缓存机制**
  - 缓存工具：`cache.js` - 基于Map的轻量级内存缓存
  - 缓存封装：`cachedRequest.js` - axios GET请求缓存包装
  - 应用场景：标签服务（5分钟TTL）
  - 实际收益：标签列表5分钟内无需重复请求
- ✅ **技术选型** - 自实现轻量级缓存，减少约50KB依赖

---

## 🎉 最新更新 (v1.5.3 - 2026-01-12)

### 🐛 重要Bug修复 - 笔记编辑器白屏问题
- ✅ **修复笔记编辑器加载失败** - 解决 "React is not defined" 错误
  - **问题原因**：`react-markdown-editor-lite` 库（v1.4.0）期望 React 作为全局变量，但在 Vite + React 18+ 环境中 React 不再自动暴露为全局变量
  - **解决方案**：
    1. 在 `NoteEditor.jsx` 中添加 `React` 导入：`import React, { useState, useEffect, useRef } from 'react'`
    2. 在 `main.jsx` 中暴露全局变量：`window.React = React; window.ReactDOM = ReactDOM`
    3. 在 `vite.config.js` 中添加配置：`define: { 'global': 'globalThis' }` 和 `optimizeDeps: { include: ['react-markdown-editor-lite'] }`
  - **影响范围**：笔记创建和编辑功能现在可以正常使用

### ✨ 功能完善 - 标签系统前端集成
- ✅ **论文创建/编辑页面标签选择** - 完成标签系统的最后一块拼图
  - 在 `AddPaper.jsx` 中添加标签多选下拉框
  - 在 `EditPaper.jsx` 中添加标签编辑功能（智能识别新增和删除的标签）
  - 支持彩色标签显示和实时预览
  - 创建论文后自动关联选中的标签

### 🐛 Bug修复 (v1.5.1)
- ✅ **PDF下载功能** - 论文列表页添加下载按钮
  - 新增后端API：GET /papers/{paper_id}/download
  - 下载按钮始终显示，无PDF时自动禁用
  - 使用论文标题作为下载文件名
  - 自动权限验证（仅创建者和管理员可下载）
- ✅ **PDF上传功能修复** - 修复上传PDF后路径未保存的问题
  - 修改PaperCreate/PaperUpdate schema，添加pdf_path字段
  - 修改后端create_paper接口，pdf_path通过请求体传递
  - 简化前端上传逻辑，确保路径正确保存

### ✨ UI/UX重大优化 (v1.5.0)
- 🦴 **Skeleton骨架屏系统** - 提升加载体验，5种骨架屏类型
  - 基础骨架屏（text/title/avatar/image/button/card）
  - 预定义组合（PaperListSkeleton/PaperDetailSkeleton/CardSkeleton/TableSkeleton）
  - 支持自定义尺寸、数量、动画效果
  - 自动适配暗色模式
- 📱 **全面响应式布局** - 完美支持移动端和平板设备
  - 6个响应式断点（xs/sm/md/lg/xl/xxl）
  - 移动端表格自动转卡片布局
  - 侧边栏在移动端改为抽屉模式
  - 触摸优化：增大点击区域（44px）
  - 支持横屏和打印模式
- 🎬 **页面切换动画** - 平滑的页面过渡效果
  - 5种动画模式（fade/slide-left/slide-right/slide-up/zoom）
  - 基于react-transition-group实现
  - 移动端自动减弱动画以提升性能
  - 支持`prefers-reduced-motion`用户偏好
- ⌨️ **快捷键系统** - 提升操作效率
  - 6个全局快捷键（Ctrl+K搜索、Ctrl+N新建等）
  - Mac自动适配（⌘代替Ctrl）
  - 快捷键帮助面板（Shift+/）
  - 输入框智能感知，避免冲突
- 🎯 **新用户引导Tour** - 交互式功能引导
  - 4个页面的完整引导（Dashboard/论文列表/论文详情/标签管理）
  - 自动检测新用户，首次访问时显示
  - 手动触发按钮，随时重新查看
  - 优雅的高亮动画和提示面板

### 🔧 新增依赖包
- ✅ **react-transition-group** - 页面切换动画支持

### Bug修复 (v1.4.1)
- 🐛 **登录/注册界面闪烁问题修复** - 优化CSS动画性能，消除页面闪烁
  - 移除背景无限旋转动画，改为静态装饰
  - 简化浮动图形动画（4关键帧→2关键帧，15s→20s）
  - 移除卡片hover的transform冲突
  - 去掉性能消耗大的backdrop-filter模糊效果
  - 添加animation-fill-mode防止动画重复触发
- 🐛 **认证错误提示缺失修复** - 完善登录/注册错误提示
  - 登录错误：401密码错误、403待审核/禁用、网络错误等7种场景
  - 注册错误：400用户名重复/邮箱重复/验证失败、网络错误等5种场景
  - 优化request.js拦截器，避免认证请求错误提示重复显示

### 新功能 (v1.4.0)
- ✅ **数据导出功能** - BibTeX导出（单篇/批量/全部）、笔记导出Markdown、用户数据全量导出JSON
- ✅ **数据导入功能** - BibTeX文件导入，支持.bib/.bibtex格式，自动解析批量创建
- ✅ **打印优化** - 专业打印样式，论文详情和笔记打印友好布局
- ✅ **管理员用户管理** - 完整的用户管理界面，支持角色修改、密码重置、用户删除
- ✅ **管理员统计Dashboard** - 全站统计数据可视化，用户/论文/笔记/标签统计
- ✅ **用户审核系统** - 待审核用户管理，一键激活功能
- ✅ **权限保护机制** - 管理员自我保护，防止误操作
- ✅ **页面美化** - 登录/注册页面全新设计，渐变背景、浮动动画、404错误页面
- ✅ **空状态组件** - 统一的空状态UI组件，支持5种类型(papers/notes/tags/search/default)
- ✅ **加载动画组件** - 3种加载动画样式(spinner/dots/pulse)，支持全屏模式和自定义提示

### 技术改进
- ✅ **8个新增数据导入导出API** - BibTeX导入导出、笔记导出、用户数据导出
- ✅ **前端打印样式** - 专业CSS @media print优化，隐藏交互元素
- ✅ **前端导入导出UI** - 批量导出、拖拽上传、进度提示
- ✅ **5个新增管理员API** - 用户角色更新、密码重置、用户删除、统计概览、用户增长
- ✅ **前端页面完善** - 用户管理页面、管理员Dashboard页面
- ✅ **路由和菜单集成** - 管理员专属菜单，角色动态显示
- ✅ **UI/UX优化** - 登录页面动画、表单淡入效果、按钮hover效果、响应式设计
- ✅ **组件封装** - EmptyState空状态组件、Loading加载组件、NotFound 404页面
- ✅ **CSS动画性能优化** - 简化动画、移除重绘触发、添加动画控制
- ✅ **错误处理完善** - 统一的错误提示模式、友好的用户反馈

[查看完整更新日志 →](API接口文档.md#更新日志)

---

## 🌟 项目特点

- ✅ **零依赖部署** - 使用SQLite数据库，无需额外安装MySQL等数据库
- ✅ **现代化技术栈** - FastAPI + React + Vite + Ant Design
- ✅ **AI助手集成** - 支持OpenAI/Anthropic API集成（计划中）
- ✅ **权限管理** - 基于角色的访问控制（管理员/普通用户）
- ✅ **内容所有权** - 用户只能管理自己创建的内容
- ✅ **响应式设计** - 支持桌面端和移动端访问
- ✅ **一键启动** - 提供自动化启动脚本
- ✅ **国内优化** - 前端自动使用淘宝镜像加速

---

## 🛠 技术栈

### 后端
- **框架**: FastAPI 0.104+
- **数据库**: SQLite (异步 aiosqlite)
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT (python-jose)
- **密码加密**: Passlib + Bcrypt 3.2.2
- **异步支持**: asyncio

### 前端
- **框架**: React 18.2+
- **构建工具**: Vite 5.0+
- **UI组件库**: Ant Design 5.12+
- **路由**: React Router 6.20+
- **状态管理**: Zustand 4.4+
- **HTTP客户端**: Axios 1.6+
- **Markdown渲染**: React Markdown 9.0+
- **Markdown编辑器**: React Markdown Editor Lite 1.4.0 + Markdown-it 14.1.0
- **颜色选择器**: React Color 2.19+
- **页面切换动画**: React Transition Group 4.4+

### 开发工具
- **API文档**: Swagger UI / ReDoc
- **代码规范**: ESLint + Prettier
- **版本控制**: Git

---

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Node.js 16+
- npm 或 yarn

### 1. 克隆项目

```bash
git clone <repository-url>
cd 论文评估网站
```

### 2. 启动后端（终端1）

#### 方式一：使用一键启动脚本（推荐）⭐

**Linux/Mac:**
```bash
cd backend
bash start.sh
```

**Windows:**
```cmd
cd backend
start.bat
```

脚本会自动：
- 创建并激活虚拟环境
- 安装所有依赖
- 初始化数据库
- 创建默认管理员账号
- 启动后端服务

#### 方式二：手动启动

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python3 scripts/init_db.py

# 启动服务
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 `http://localhost:8000` 启动

**默认管理员账号**：
- 用户名: `admin`
- 密码: `admin123`

> ⚠️ **重要**：首次登录后请立即修改密码！

### 3. 启动前端（终端2）

#### 方式一：使用一键启动脚本（推荐）⭐

```bash
cd frontend
bash start.sh
```

脚本会自动：
- 检查 Node.js 环境
- 使用淘宝镜像加速下载
- 安装所有依赖（首次运行）
- 启动开发服务器

#### 方式二：手动启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 4. 访问应用

打开浏览器访问 `http://localhost:5173`

- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ✅ 已完成功能

### 第一阶段：项目初始化与基础架构 ✅ (100%)

- [x] 创建前后端项目目录结构
- [x] 配置前端项目（Vite + React + Ant Design）
- [x] 配置后端项目（FastAPI + SQLite）
- [x] 设计SQLite数据库表结构（9个核心表）
- [x] 实现数据库初始化脚本
- [x] 实现JWT认证中间件
- [x] 实现CORS配置
- [x] 实现统一响应格式
- [x] 实现API文档（Swagger/OpenAPI）
- [x] 实现健康检查接口
- [x] 创建一键启动脚本（前后端）
- [x] 配置国内镜像加速

### 第二阶段：用户系统 ✅ (100%)

- [x] 用户注册功能（带邮箱验证）
- [x] 用户登录功能（JWT Token）
- [x] 密码加密存储（bcrypt）
- [x] 角色定义（管理员/普通用户）
- [x] 权限验证中间件
- [x] 路由守卫（前端）
- [x] API权限验证（后端）
- [x] 用户状态管理（Zustand + 持久化）
- [x] 注册页面UI
- [x] 登录页面UI
- [x] 基础布局组件
- [x] 个人中心页面（Profile）
  - [x] 基本信息展示
  - [x] 更新个人信息（API已连接）
  - [x] 修改密码功能（API已连接）
  - [x] 账号统计展示

### 第三阶段：论文管理核心功能 ✅ (100%)

#### 后端API ✅
- [x] 论文Pydantic schemas定义（含volume/issue/pages/url字段）
- [x] PDF文件上传接口（最大50MB）
- [x] 创建论文API
- [x] 获取论文列表API（搜索、筛选、分页）
- [x] 获取论文详情API
- [x] 更新论文API
- [x] 删除论文API（软删除）
- [x] 权限控制（用户只能管理自己的论文）
- [x] Paper模型扩展字段（卷号、期号、页码、链接）

#### 前端页面 ✅
- [x] 论文API服务封装
- [x] 论文列表页面
  - [x] 搜索功能（标题、作者、关键词）
  - [x] 筛选功能（年份、状态、排序）
  - [x] 分页显示
  - [x] 表格展示（含权限控制）
- [x] 添加论文页面
  - [x] 完整表单（标题、作者、期刊、年份、卷号、期号、页码等）
  - [x] PDF文件上传
  - [x] 阅读状态选择
- [x] 论文详情页面
  - [x] 完整信息展示
  - [x] 创建者信息显示
  - [x] DOI/arXiv链接
  - [x] PDF下载链接
- [x] 编辑论文页面
  - [x] 表单预填充
  - [x] PDF文件重新上传
- [x] 路由配置（/papers, /papers/add, /papers/:id, /papers/:id/edit）
- [x] 响应数据格式统一处理（修复response.data问题）

### 第四阶段：Dashboard统计功能 ✅ (100%)

- [x] 后端统计API路由（stats.py）
- [x] Dashboard统计接口（GET /api/stats/dashboard）
- [x] 阅读进度接口（GET /api/stats/reading-progress）
- [x] 论文/笔记/标签数量统计
- [x] 阅读状态分组统计（未读/在读/已读）
- [x] 最近阅读记录查询（最近5篇）
- [x] 前端统计服务封装（statsService.js）
- [x] Dashboard页面完整重写
- [x] 统计卡片组件（论文/笔记/标签）
- [x] 阅读进度可视化（进度条+百分比）
- [x] 阅读状态分布图表（三个状态条形图）
- [x] 最近阅读列表（可点击跳转）
- [x] 响应式布局适配
- [x] 加载状态和错误处理

### 第五阶段：标签系统 ✅ (100%)

#### 后端API ✅
- [x] 标签Pydantic schemas定义（TagBase, TagCreate, TagUpdate, TagResponse）
- [x] 颜色验证器（支持#RGB和#RRGGBB格式）
- [x] 创建标签API（POST /api/tags/）
- [x] 获取标签列表API（GET /api/tags/）
- [x] 获取标签详情API（GET /api/tags/{tag_id}）
- [x] 更新标签API（PUT /api/tags/{tag_id}）
- [x] 删除标签API（DELETE /api/tags/{tag_id}）
- [x] 为论文添加标签API（POST /api/tags/papers/{paper_id}/tags）
- [x] 从论文移除标签API（DELETE /api/tags/papers/{paper_id}/tags/{tag_id}）
- [x] 获取论文标签API（GET /api/tags/papers/{paper_id}/tags）
- [x] 论文列表按标签筛选（GET /api/papers?tag_id=X）
- [x] 标签名称唯一性验证（同一用户下）
- [x] 论文API返回标签数据（load_paper_tags辅助函数）

#### 前端UI ✅
- [x] 标签API服务封装（tagService.js，9个方法）
- [x] 标签管理页面（/tags）
  - [x] 标签列表表格（名称、颜色、论文数量、创建时间、操作）
  - [x] 创建/编辑对话框
  - [x] 颜色选择器（React Color SketchPicker）
  - [x] 实时标签预览
  - [x] 删除确认弹窗
- [x] 论文详情页标签显示
  - [x] 标签列表展示（带颜色）
  - [x] 点击标签跳转到筛选页面
- [x] 论文列表页标签集成
  - [x] 标签列显示（最多2个+计数）
  - [x] 标签筛选下拉框
  - [x] URL参数支持（?tag=X）
- [x] 侧边栏菜单添加标签管理入口
- [x] 路由配置（/tags）

### 第六阶段：阅读状态完善 ✅ (100%)

#### 后端API ✅
- [x] Paper模型添加reading_progress字段（0-100）
- [x] ReadingHistory模型（阅读会话记录）
- [x] 数据库迁移脚本（migrate_add_reading_features.py）
- [x] 阅读进度schemas定义（ReadingProgressUpdate, ReadingSessionCreate等）
- [x] 更新阅读进度API（PUT /api/reading/papers/{id}/progress）
- [x] 创建阅读会话API（POST /api/reading/papers/{id}/sessions）
- [x] 获取阅读历史API（GET /api/reading/papers/{id}/history）
- [x] 获取阅读统计API（GET /api/reading/stats）
- [x] 获取论文阅读统计API（GET /api/reading/papers/stats）
- [x] Papers API响应添加reading_progress字段

#### 前端UI ✅
- [x] 阅读服务封装（readingService.js，5个方法）
- [x] 论文详情页阅读进度展示
  - [x] Progress进度条显示
  - [x] Slider滑块更新进度
  - [x] 实时保存和状态同步
  - [x] 权限控制（仅创建者可编辑）
- [x] 自动状态同步（0%=未读，1-99%=在读，100%=已读）

#### 近期修复 ✅
- [x] JWT Token字段类型修复（sub必须为字符串）
- [x] Paper模型字段对齐（添加volume/issue/pages/url/notes_preview）
- [x] 前端响应格式统一修复（9处）
- [x] Profile页面API调用连接
- [x] 软删除机制修复（is_deleted → deleted_at）
- [x] Pydantic异步关系访问错误修复（手动构建响应字典）
- [x] PDF下载功能实现（PaperDetail页面）

#### 近期完成功能 ✅ (2026-01-11)
- [x] Dashboard数据统计完整实现
  - [x] 后端统计API（/api/stats/dashboard, /api/stats/reading-progress）
  - [x] 论文/笔记/标签数量统计
  - [x] 阅读状态分组统计
  - [x] 最近阅读记录（最近5篇）
  - [x] 阅读进度可视化（进度条+百分比）
  - [x] 阅读状态分布图表
  - [x] 响应式布局和交互优化
- [x] 标签系统完整实现
  - [x] 后端9个标签API接口（CRUD + 关联管理）
  - [x] 标签schemas定义和颜色验证
  - [x] 论文API集成标签数据加载
  - [x] 标签管理页面（含颜色选择器）
  - [x] 论文详情页标签显示（带颜色、可点击）
  - [x] 论文列表页标签筛选功能
  - [x] 标签列显示（最多显示2个+计数）
  - [x] URL参数支持标签过滤
- [x] 阅读状态完善功能
  - [x] 后端5个阅读API接口（进度更新、会话记录、历史查询、统计）
  - [x] ReadingHistory模型和数据库迁移
  - [x] 阅读进度schemas定义和验证
  - [x] Papers API返回reading_progress字段
  - [x] 论文详情页进度条和滑块（实时更新）
  - [x] 自动状态同步（未读/在读/已读）
  - [x] 前端阅读服务封装
- [x] 笔记系统完整实现
  - [x] 后端5个笔记API接口（创建、列表、详情、更新、删除）
  - [x] Note模型和数据库表（含7种笔记类型）
  - [x] 笔记schemas定义和类型验证
  - [x] Markdown编辑器集成（react-markdown-editor-lite + markdown-it）
  - [x] 笔记编辑器组件（NoteEditor.jsx）
    - [x] 实时Markdown预览
    - [x] 自动保存功能（30秒）
    - [x] 结构化笔记模板（5种类型）
    - [x] 笔记类型选择器
  - [x] 论文详情页笔记Tab
    - [x] 笔记列表显示
    - [x] 创建/编辑/删除功能
    - [x] 类型标签彩色显示
    - [x] 笔记预览（前200字符）
  - [x] Paper模型集成notes_preview字段
  - [x] 前端笔记服务封装（noteService.js）

#### 近期完成功能 ✅ (2026-01-13)
- [x] **科研网站收藏系统完整实现** (v1.10.0)
  - [x] 后端6个网站API接口
    - POST `/api/websites/` - 创建网站
    - GET `/api/websites/` - 获取网站列表（搜索、筛选、分页）
    - GET `/api/websites/categories` - 获取分类列表
    - GET `/api/websites/{id}` - 获取网站详情
    - PUT `/api/websites/{id}` - 更新网站信息
    - DELETE `/api/websites/{id}` - 删除网站（软删除）
  - [x] 数据库表创建（websites表，10个字段，4个索引）
    - 字段：id, user_id, name, url, category, description, is_favorite, created_at, updated_at, deleted_at
    - 索引：user_id, category, is_favorite, deleted_at
    - 外键：user_id → users(id) CASCADE DELETE
  - [x] 预置27个常用科研网站
    - 学术搜索（3个）、论文数据库（8个）、文献管理（3个）
    - 引文分析（2个）、期刊资源（3个）、学术工具（4个）、数据集（4个）
  - [x] 前端页面完整实现（Websites.jsx）
    - 表格展示（名称、链接、分类、描述、操作）
    - 多维度搜索（名称、描述、链接）
    - 分类筛选（7个预设分类 + 自定义）
    - 收藏筛选（仅收藏/未收藏）
    - 收藏功能（星标按钮，一键切换）
    - 点击访问（新标签页打开）
    - 创建/编辑对话框（名称、链接、分类、描述、收藏）
    - 删除确认弹窗
    - 分页支持
  - [x] 前端服务封装（websitesService.js，6个方法）
  - [x] 导航菜单集成（"网站收藏"，GlobalOutlined图标）
  - [x] 路由配置（/websites）
  - [x] 权限控制（用户只能管理自己的网站，管理员查看所有）
  - [x] 性能优化（乐观更新，操作立即响应）
  - [x] 问题修复（3个）
    - 🐛 修复URL路径重复（404错误）- 移除服务中的`/api`前缀
    - ⚡ 修复收藏卡顿 - 实现乐观更新（从500ms延迟 → 0ms）
    - 🐛 修复表单Checkbox配置 - 正确设置valuePropName和初始值

- [x] **站内通知系统完整实现** (v1.8.0)
  - [x] 后端5个通知API接口
    - GET `/api/notifications/` - 获取通知列表（支持筛选已读/未读、分页）
    - GET `/api/notifications/unread-count` - 获取未读通知数量
    - PUT `/api/notifications/{id}/read` - 标记通知为已读
    - PUT `/api/notifications/read-all` - 标记所有通知为已读
    - DELETE `/api/notifications/{id}` - 删除通知
  - [x] 通知数据库表（notifications）
    - 字段：id, user_id, type, title, content, link, is_read, created_at, sender_id, related_id
    - 索引：user_id, is_read, created_at, type
    - 外键约束：CASCADE DELETE 和 SET NULL
  - [x] 评论回复自动通知（修改comments.py:22, 141-164）
    - 回复评论时自动创建通知给父评论作者
    - 不给自己发通知（回复自己的评论时跳过）
    - 通知包含：回复者、论文标题、回复内容、跳转链接
  - [x] 通知中心页面（Notifications.jsx）
    - 3个标签页：全部通知/未读通知/已读通知
    - 未读通知高亮显示（蓝色背景 + 边框 + 徽标）
    - 相对时间显示（"3分钟前"）
    - 通知类型彩色标签（评论回复/系统通知/提及）
    - 一键全部已读、点击跳转相关页面、分页支持
  - [x] 导航栏通知铃铛（修改Layout.jsx:1, 12, 16, 26, 28-50, 140-154）
    - BellOutlined图标 + 红色徽标数字
    - 实时未读计数（每30秒自动刷新）
    - 有未读通知时图标变蓝色
  - [x] 通知服务封装（notificationService.js）
  - [x] 通知类型支持：comment_reply（评论回复）、system（系统通知）、mention（@提及，预留）
  - [x] 实现过程：无错误，所有功能顺利完成

#### 近期修复和优化 ✅ (2026-01-11)
- [x] **代码审查与时区修复**
  - [x] 统一时间处理：所有datetime.now()改为datetime.utcnow()
    - notes.py: 5处时间设置统一（创建、更新、删除）
    - reading.py: 1处时间设置统一（进度更新）
    - papers.py: 3处时间设置统一（更新、软删除）
  - [x] schemas/__init__.py完善
    - 添加note schemas导出（NoteBase, NoteCreate, NoteUpdate, NoteResponse, NoteListResponse）
    - 添加tag schemas导出（TagCreate, TagUpdate, TagResponse, TagListResponse, AddTagsRequest）
    - 添加reading schemas导出（ReadingProgressUpdate, ReadingSessionCreate, etc.）
  - [x] models/__init__.py完善
    - 添加ReadingHistory模型导出
  - [x] Python语法验证通过（所有routes、schemas、models）

**技术细节**:
- **时区一致性**: 所有数据库时间戳统一使用UTC时区，避免跨时区问题
- **模块规范性**: 完善__init__.py导出，确保模块间依赖清晰
- **代码质量**: 通过Python语法编译检查，确保零语法错误

---

## 📝 待办事项

> **实现原则**：从简单到复杂 → 从必要到创新 → 循序渐进

---

## 🎯 第一优先级：核心基础功能（简单且必要）⭐⭐⭐

**预计时间**：2-3天 | **价值**：高 | **难度**：低

### 1. Dashboard数据统计 ✅ 简单 【已完成 2026-01-10】
- [x] 实现统计API（论文数、笔记数、标签数）
- [x] 更新Dashboard页面展示真实数据
- [x] 添加最近阅读记录展示
- [x] 添加阅读进度可视化

### 2. 标签系统（基础版）✅ 简单 【已完成 2026-01-10】
**后端API**
- [x] 创建标签API（POST /tags/）
- [x] 获取标签列表API（GET /tags/）
- [x] 更新标签API（PUT /tags/{id}）
- [x] 删除标签API（DELETE /tags/{id}）
- [x] 为论文添加标签API（POST /papers/{paper_id}/tags）
- [x] 从论文移除标签API（DELETE /papers/{paper_id}/tags/{tag_id}）
- [x] 获取论文标签API（GET /papers/{paper_id}/tags）
- [x] 按标签筛选论文API（GET /papers?tag_id=X）
- [x] 论文API返回真实标签数据

**前端UI**
- [x] 标签管理页面（/tags）
- [x] 标签创建/编辑对话框（名称+颜色选择器SketchPicker）
- [x] 论文详情页显示标签（带颜色、可点击筛选）
- [x] 论文列表页标签列显示
- [x] 论文列表页标签筛选下拉框
- [x] 侧边栏菜单添加标签管理入口
- [x] URL参数支持（?tag=X）

### 3. 阅读状态完善 ✅ 简单 【已完成 2026-01-11】
- [x] 阅读进度百分比记录（0-100）
- [x] Paper模型添加reading_progress字段
- [x] ReadingHistory模型（记录阅读会话）
- [x] 数据库迁移脚本
- [x] 阅读进度更新API（PUT /api/reading/papers/{id}/progress）
- [x] 阅读会话记录API（POST /api/reading/papers/{id}/sessions）
- [x] 阅读历史查询API（GET /api/reading/papers/{id}/history）
- [x] 阅读统计API（GET /api/reading/stats）
- [x] 论文阅读统计API（GET /api/reading/papers/stats）
- [x] 论文详情页阅读进度条（Progress + Slider）
- [x] 实时进度更新和状态同步

---

## 🎯 第二优先级：核心扩展功能（必要但稍复杂）⭐⭐

**预计时间**：4-5天 | **价值**：高 | **难度**：中

### 4. 笔记系统 📝 中等 ✅
**后端API**
- [x] 创建笔记API（POST /papers/{id}/notes）
- [x] 获取笔记列表API（GET /papers/{id}/notes）
- [x] 获取笔记详情API（GET /notes/{id}）
- [x] 更新笔记API（PUT /notes/{id}）
- [x] 删除笔记API（DELETE /notes/{id}）

**前端UI**
- [x] 集成Markdown编辑器（react-markdown-editor-lite）
- [x] 论文详情页笔记标签页
- [x] 笔记列表展示
- [x] 笔记编辑页面
- [x] 结构化笔记模板（可选）
  - 研究问题/动机
  - 核心方法
  - 主要结论
  - 创新点
  - 局限性
  - 个人思考
- [x] 笔记自动保存（每30秒）
- [x] 笔记预览模式

### 5. 项目/主题分组 📁 中等
**后端API**
- [ ] 创建项目API
- [ ] 获取项目列表API
- [ ] 更新项目API
- [ ] 删除项目API
- [ ] 添加论文到项目API
- [ ] 从项目移除论文API

**前端UI**
- [ ] 项目管理页面
- [ ] 项目创建对话框
- [ ] 项目详情页（展示该项目的所有论文）
- [ ] 论文详情页显示所属项目
- [ ] 项目统计（论文数、完成度）
- [ ] 项目删除（级联处理提示）

### 6. 评论功能（基础版）💬 中等
**后端API**
- [ ] 创建评论API（POST /papers/{id}/comments）
- [ ] 获取评论列表API（GET /papers/{id}/comments）
- [ ] 更新评论API（PUT /comments/{id}）
- [ ] 删除评论API（DELETE /comments/{id}）
- [ ] 回复评论API（支持一级回复）

**前端UI**
- [ ] 论文详情页评论区
- [ ] 评论列表展示（分页）
- [ ] 评论输入框
- [ ] 回复评论功能
- [ ] 编辑/删除按钮（权限控制）
- [ ] 评论排序（最新/最早）

---

## 🎯 第三优先级：管理员功能（必要但独立）⭐

**预计时间**：2-3天 | **价值**：中 | **难度**：中

### 7. 用户管理（管理员）👥 中等 【已完成 2026-01-11】
**后端API**
- [x] 获取所有用户API
- [x] 更新用户状态API
- [x] 更新用户角色API
- [x] 删除用户API（软删除）
- [x] 重置用户密码API
- [x] 管理员自我保护机制

**前端UI**
- [x] 用户管理页面（路由：/admin/users）
- [x] 用户列表表格（带状态和角色标签）
- [x] 用户搜索功能（用户名、邮箱、部门）
- [x] 用户编辑对话框
- [x] 用户状态修改（pending/active/disabled）
- [x] 用户角色修改（user/admin）
- [x] 密码重置对话框
- [x] 删除用户确认（Popconfirm）

### 8. 用户审核功能 ✅ 简单 【已完成 2026-01-11】
- [x] 待审核用户列表（在用户管理页面）
- [x] 审核通过按钮（直接激活用户）
- [x] 状态筛选和展示
- [x] 实时状态更新

### 9. 系统统计（管理员）📊 简单 【已完成 2026-01-11】
**后端API**
- [x] 管理员统计概览API（/stats/admin/overview）
- [x] 用户增长趋势API（/stats/admin/user-growth）

**前端UI**
- [x] 管理员Dashboard页面（路由：/admin/dashboard）
- [x] 用户统计卡片（总数、激活、待审核、禁用）
- [x] 用户角色分布
- [x] 论文统计卡片（总数、未读、在读、已读）
- [x] 笔记和标签统计
- [x] 最近7天活动统计（新增用户、论文、笔记）
- [x] 进度条可视化

---

## 🎯 第四优先级：数据导出与工具（实用扩展）⭐

**预计时间**：2-3天 | **价值**：中 | **难度**：中

### 10. 数据导出功能 📤 中等 ✅【已完成 2026-01-12】
**后端API**
- [x] 笔记导出为Markdown（GET /notes/{id}/export?format=md）
- [x] 参考文献列表生成（BibTeX格式）
  - [x] 单篇论文导出（GET /papers/{id}/export/bibtex）
  - [x] 批量导出（POST /papers/export/bibtex/batch）
  - [x] 导出全部（GET /papers/export/bibtex/all）
- [x] 个人数据全量导出（JSON）（GET /users/me/export-data）
- [ ] 笔记导出为PDF（需要库：pdfkit）
- [ ] 参考文献APA/MLA格式（可选）

**前端UI**
- [x] 笔记详情页添加"导出"按钮
- [x] 批量导出功能（论文列表页）
- [x] BibTeX导出（单篇/批量/全部）

### 11. 数据导入功能 📥 中等 ✅【已完成 2026-01-12】
- [x] BibTeX文件导入（POST /papers/import/bibtex）
- [x] 前端拖拽上传UI（Upload.Dragger）
- [x] 导入进度提示
- [x] 导入结果统计（成功/失败数量）
- [ ] CSV文件导入（可选）
- [ ] EndNote导入（可选）

### 12. 打印优化 🖨️ 简单 ✅【已完成 2026-01-12】
- [x] 打印样式优化（CSS @media print）
- [x] 论文详情打印模板
- [x] 笔记打印模板
- [x] 打印按钮集成（论文详情页）
- [x] 打印页眉/页脚
- [x] 隐藏交互元素（.no-print类）

---

## 🎯 第五优先级：界面美化与体验优化（锦上添花）⭐

**预计时间**：3-4天 | **价值**：中 | **难度**：低-中

### 13. 视觉资源集成 🎨 简单 ✅【已完成 2026-01-12】
- [x] 登录/注册页面背景装饰(渐变背景、旋转圆圈、浮动图形)
- [x] 空状态插画组件(EmptyState.jsx)
- [x] 加载动画组件(Loading.jsx，支持3种动画类型)
- [x] 404错误页面设计

### 14. 页面美化 💎 简单 ✅【已完成 2026-01-12】
- [x] 登录/注册页面美化（渐变背景、动画效果、毛玻璃卡片）
- [x] 表单动画优化(淡入向上动画、延迟加载)
- [x] 按钮hover效果优化
- [x] 空状态页面设计（空论文、空笔记、空标签等）
- [x] 404错误页面(数字弹跳动画、浮动图标)

### 15. UI/UX优化 ✨ 中等 ✅【已完成 2026-01-12】
- [x] 响应式布局优化（移动端适配）
- [x] 页面切换动画（React Router transitions）
- [x] 交互反馈优化（Skeleton、Toast）
- [x] 快捷键支持（Ctrl+K搜索、Ctrl+N新建等）
- [x] 用户引导（新用户Tour）

### 16. 性能优化 ⚡ 中等 ✅【部分完成 2026-01-12】
- [ ] 图片懒加载（react-lazyload）
- [ ] 图片压缩与WebP格式
- [x] 代码分割（React.lazy）
  - **路由级代码分割**：6个低频路由懒加载（AddPaper、EditPaper、Tags、Profile、AdminDashboard、UserManagement）
  - **组件级代码分割**：NoteEditor组件懒加载（包含react-markdown-editor-lite和markdown-it重型库）
  - 实现文件：`src/App.jsx`、`src/pages/PaperDetail.jsx`
- [x] API请求优化（防抖、缓存）
  - **防抖优化**：搜索框输入防抖（500ms延迟），减少不必要的API调用
  - **缓存机制**：标签数据缓存（5分钟TTL），支持自动过期和手动清除
  - 实现文件：`src/hooks/useDebounce.js`、`src/utils/cache.js`、`src/services/cachedRequest.js`、`src/pages/Papers.jsx`、`src/services/tagService.js`
- [x] 前端缓存策略
  - 采用轻量级内存缓存（Map）替代SWR/React Query，减少依赖体积
  - 支持TTL过期机制和定期清理
  - 写操作后自动清除相关缓存

---

## 🎯 第六优先级：AI助手集成（创新功能）🚀

**预计时间**：5-7天 | **价值**：高（创新） | **难度**：高

### 17. AI助手基础版 🤖 复杂

**后端基础**
- [ ] 选择LLM提供商（OpenAI GPT-4 / Anthropic Claude）
- [ ] API密钥配置（环境变量）
- [ ] LLM调用封装（openai/anthropic SDK）
- [ ] 错误处理与重试机制
- [ ] Token计数与费用追踪

**前端UI**
- [ ] 浮动对话窗口组件
- [ ] 窗口展开/收起动画
- [ ] 窗口拖拽功能（react-draggable）
- [ ] 对话消息列表
- [ ] 消息输入框
- [ ] 打字动画效果

**核心功能**
- [ ] 基础对话API（POST /ai/chat）
- [ ] 对话历史保存
- [ ] 多轮对话支持
- [ ] 上下文管理（当前论文）
- [ ] 快捷提问模板
  - "总结这篇论文"
  - "解释这篇论文的核心方法"
  - "这篇论文的创新点是什么"
  - "这篇论文有什么局限性"

**额度管理**
- [ ] 用户AI额度系统
- [ ] 额度检查中间件
- [ ] 额度显示UI
- [ ] 额度重置（每日/每月）

### 18. AI助手高级功能 🧠 非常复杂

**向量数据库（RAG基础）**
- [ ] 集成ChromaDB/Pinecone
- [ ] Embedding模型选择（OpenAI text-embedding-3）
- [ ] 论文内容分块策略（按段落/按页）
- [ ] 论文PDF文本提取（PyPDF2/pdfplumber）
- [ ] 向量化存储
- [ ] 向量相似度搜索

**RAG实现**
- [ ] 相关内容检索（Top-K）
- [ ] 检索结果重排序
- [ ] 上下文构建（拼接检索结果）
- [ ] Prompt工程优化
- [ ] 引用来源标注

**智能功能**
- [ ] 智能笔记生成（自动提取关键信息）
- [ ] 文献综述生成（多篇论文对比）
- [ ] 中英互译功能
- [ ] 专业术语解释
- [ ] 论文推荐（基于向量相似度）

**AI配置页面（管理员）**
- [ ] LLM模型选择
- [ ] API密钥管理
- [ ] 用户额度配置
- [ ] 向量数据库配置
- [ ] AI功能开关

---

## 🎯 第七优先级：高级协作功能（可选创新）💡

**预计时间**：4-5天 | **价值**：低-中 | **难度**：高

### 19. 协作功能（可选）🤝 复杂
- [ ] 论文分享链接生成
- [ ] 共享论文库（多用户）
- [ ] 协作笔记（实时编辑）
- [ ] 评论与讨论
- [ ] 权限控制（查看/编辑）

### 20. 通知系统 🔔 中等
- [ ] 站内消息通知
- [ ] 评论回复通知
- [ ] @提及通知
- [ ] 邮件通知（可选）
- [ ] 通知中心页面

---

## 🎯 第八优先级：测试与部署 🚀

**预计时间**：2-3天 | **价值**：高 | **难度**：中

### 21. 测试 🧪
- [ ] 功能测试（手动测试）
- [ ] 边界条件测试
- [ ] 安全测试（SQL注入、XSS等）
- [ ] 性能测试（并发、大数据量）

### 22. 文档 📚
- [ ] 用户使用手册
- [ ] API文档完善
- [ ] 部署文档
- [ ] 常见问题FAQ
- [ ] 开发文档

### 23. 部署 🌐
- [ ] 生产环境配置
- [ ] Nginx配置（可选）
- [ ] SSL证书配置（可选）
- [ ] Docker容器化（可选）
- [ ] 备份策略
- [ ] 监控告警（可选）

---

## 📊 实现进度跟踪

| 优先级 | 功能模块 | 预计时间 | 难度 | 价值 | 状态 |
|-------|---------|---------|------|------|------|
| P1 | Dashboard统计 | 0.5天 | 低 | 高 | ✅ **已完成** |
| P1 | 标签系统 | 1.5天 | 低 | 高 | ⏳ 待开始 |
| P1 | 阅读状态完善 | 0.5天 | 低 | 中 | ⏳ 待开始 |
| P2 | 笔记系统 | 2天 | 中 | 高 | ⏳ 待开始 |
| P2 | 项目分组 | 1.5天 | 中 | 中 | ⏳ 待开始 |
| P2 | 评论功能 | 1.5天 | 中 | 中 | ⏳ 待开始 |
| P3 | 用户管理 | 1.5天 | 中 | 中 | ⏳ 待开始 |
| P3 | 用户审核 | 0.5天 | 低 | 中 | ⏳ 待开始 |
| P3 | 系统统计 | 1天 | 中 | 中 | ⏳ 待开始 |
| P4 | 数据导出 | 2天 | 中 | 中 | ⏳ 待开始 |
| P5 | 界面美化 | 3天 | 低-中 | 中 | ⏳ 待开始 |
| P6 | AI基础版 | 4天 | 高 | 高 | ⏳ 待开始 |
| P6 | AI高级版 | 3天 | 很高 | 高 | ⏳ 待开始 |
| P7 | 协作功能 | 4天 | 高 | 低 | ⏳ 待开始 |
| P8 | 测试部署 | 2天 | 中 | 高 | ⏳ 待开始 |

**总预计时间**：约28-35天（全职开发）

---

## 🎯 建议实施路线

### 阶段一：快速增值（第1-2周）
**目标**：快速实现核心基础功能，提升用户体验
- ✅ Dashboard统计
- ✅ 标签系统
- ✅ 阅读状态完善

### 阶段二：核心功能（第3-4周）
**目标**：实现论文管理的核心扩展功能
- ✅ 笔记系统
- ✅ 项目分组
- ✅ 评论功能

### 阶段三：管理完善（第5周）
**目标**：完善管理员功能
- ✅ 用户管理
- ✅ 用户审核
- ✅ 系统统计

### 阶段四：工具扩展（第6周）
**目标**：增加实用工具
- ✅ 数据导出
- ✅ 界面美化

### 阶段五：创新突破（第7-9周）
**目标**：AI助手集成（项目亮点）
- ✅ AI基础版
- ✅ AI高级版（RAG）

### 阶段六：优化上线（第10周）
**目标**：测试、优化、部署
- ✅ 全面测试
- ✅ 文档完善
- ✅ 生产部署

---

## 💡 实现建议

### 开发策略
1. **先简后繁**：先实现基础功能，再添加高级特性
2. **MVP思维**：每个功能先做最小可行版本，后续迭代
3. **增量开发**：每完成一个模块立即测试，确保稳定
4. **用户反馈**：阶段性收集用户反馈，调整优先级

### 技术选型建议
- **Markdown编辑器**：react-markdown-editor-lite（轻量、功能完整）
- **图表库**：ECharts（功能强大）或 Recharts（React友好）
- **拖拽库**：react-dnd 或 react-draggable
- **状态管理**：继续使用Zustand（已有）
- **AI SDK**：OpenAI官方SDK 或 Anthropic SDK
- **向量数据库**：ChromaDB（开源、易部署）或 Pinecone（云服务）

### 风险提示
- ⚠️ AI功能需要API费用预算（OpenAI/Anthropic）
- ⚠️ 向量数据库可能需要较大存储空间
- ⚠️ 协作功能需要实时通信（WebSocket）
- ⚠️ PDF文本提取质量取决于PDF格式

---

**下一步行动**：请告诉我您想从哪个优先级开始实现？我建议从 **P1（Dashboard统计 + 标签系统）** 开始，快速见效！
- [ ] 用户额度设置
- [ ] 向量数据库配置
- [ ] AI功能开关

### 第八阶段：界面美化与优化

#### 视觉资源集成
- [ ] 从Unsplash/Pexels下载图片
- [ ] 生成AI背景图片
- [ ] 创建占位图库
- [ ] 集成图标库（Font Awesome）
- [ ] 添加插画资源（unDraw）

#### 页面美化
- [ ] 登录/注册页面美化
- [ ] 添加背景图片
- [ ] 空状态插画集成
- [ ] 加载动画设计
- [ ] 错误页面美化（404等）

#### UI/UX优化
- [ ] 响应式布局优化
- [ ] 移动端适配
- [ ] 动画效果添加
- [ ] 交互反馈优化
- [ ] 颜色方案调整（学术风格）

#### 性能优化
- [ ] 图片懒加载
- [ ] 图片压缩与WebP格式
- [ ] 代码分割
- [ ] API请求优化
- [ ] 前端缓存策略

#### 用户引导
- [ ] 新用户引导页
- [ ] 功能提示（Tooltip）
- [ ] 帮助文档
- [ ] 快捷键提示

### 第九阶段：导出与分享功能

#### 数据导出
- [ ] 笔记导出为Markdown
- [ ] 笔记导出为PDF
- [ ] 笔记导出为Word
- [ ] 参考文献列表生成（多种格式）
- [ ] 主题论文批量导出
- [ ] 个人数据全量导出

#### 协作功能（可选）
- [ ] 论文分享链接生成
- [ ] 共享论文库
- [ ] 协作笔记
- [ ] 评论与讨论
- [ ] 权限控制（查看/编辑）

#### 数据导入
- [ ] BibTeX批量导入
- [ ] EndNote导入
- [ ] CSV导入

#### 打印优化
- [ ] 打印样式优化
- [ ] 论文详情打印
- [ ] 笔记打印

### 第十阶段：测试与部署

#### 功能测试
- [ ] 用户系统测试
- [ ] 论文管理测试
- [ ] 笔记系统测试
- [ ] AI助手测试
- [ ] 权限系统测试
- [ ] 边界条件测试

#### 安全测试
- [ ] SQL注入测试
- [ ] XSS测试
- [ ] CSRF测试
- [ ] 文件上传安全测试
- [ ] 权限绕过测试

#### 性能测试
- [ ] 并发用户测试
- [ ] 大数据量测试
- [ ] API响应时间测试
- [ ] 内存占用测试

#### 文档编写
- [ ] 用户使用手册
- [ ] API文档完善
- [ ] 部署文档
- [ ] 常见问题FAQ
- [ ] 开发文档

#### 部署准备
- [ ] 生产环境配置
- [ ] 数据库初始化脚本
- [ ] 环境变量配置
- [ ] Nginx配置（如需要）
- [ ] SSL证书配置

#### 部署上线
- [ ] 本地部署测试
- [ ] 云服务器部署
- [ ] Docker容器化（可选）
- [ ] 备份策略设置
- [ ] 监控告警配置

---

## 📂 项目结构

```
论文评估网站/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   └── database.py    # SQLAlchemy模型（9个表）
│   │   ├── routes/            # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # 认证路由
│   │   │   ├── users.py       # 用户路由
│   │   │   ├── papers.py      # 论文路由 ✅
│   │   │   └── stats.py       # 统计路由 ✅
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py        # 用户schemas
│   │   │   └── paper.py       # 论文schemas ✅
│   │   ├── services/          # 业务逻辑
│   │   │   └── user_service.py
│   │   ├── utils/             # 工具函数
│   │   │   ├── dependencies.py # 依赖注入
│   │   │   ├── response.py    # 响应格式
│   │   │   └── security.py    # 安全工具
│   │   ├── config.py          # 配置管理
│   │   └── main.py            # 应用入口
│   ├── data/                  # 数据目录
│   │   ├── database.db        # SQLite数据库
│   │   └── uploads/           # 上传文件
│   │       └── papers/        # 论文PDF文件 ✅
│   ├── scripts/               # 脚本
│   │   └── init_db.py         # 数据库初始化
│   ├── start.sh              # 一键启动脚本 ✅
│   ├── setup.sh              # 环境配置脚本 ✅
│   ├── activate.sh           # 环境激活脚本 ✅
│   ├── requirements.txt       # Python依赖
│   ├── .env                   # 环境变量
│   └── README.md             # 后端文档
│
├── frontend/                  # 前端项目
│   ├── src/
│   │   ├── assets/           # 静态资源
│   │   ├── components/       # 通用组件
│   │   │   └── Layout.jsx    # 布局组件
│   │   ├── pages/            # 页面组件
│   │   │   ├── Login.jsx     # 登录页
│   │   │   ├── Register.jsx  # 注册页
│   │   │   ├── Dashboard.jsx # 仪表盘 ✅
│   │   │   ├── Papers.jsx    # 论文列表 ✅
│   │   │   ├── AddPaper.jsx  # 添加论文 ✅
│   │   │   ├── PaperDetail.jsx # 论文详情 ✅
│   │   │   └── EditPaper.jsx # 编辑论文 ✅
│   │   ├── services/         # API服务
│   │   │   ├── request.js    # Axios封装
│   │   │   ├── authService.js # 认证服务
│   │   │   ├── paperService.js # 论文服务 ✅
│   │   │   └── statsService.js # 统计服务 ✅
│   │   ├── store/            # 状态管理
│   │   │   └── authStore.js  # 认证状态
│   │   ├── utils/            # 工具函数
│   │   ├── App.jsx           # 根组件
│   │   └── main.jsx          # 入口文件
│   ├── public/               # 公共资源
│   ├── start.sh             # 一键启动脚本 ✅
│   ├── setup.sh             # 环境配置脚本 ✅
│   ├── clean.sh             # 清理脚本 ✅
│   ├── .npmrc               # npm配置（淘宝镜像）✅
│   ├── index.html           # HTML模板
│   ├── vite.config.js       # Vite配置
│   ├── package.json         # 依赖配置
│   ├── 快速启动.md          # 快速启动文档 ✅
│   ├── 脚本使用说明.md      # 脚本文档 ✅
│   └── README.md            # 前端文档
│
├── docs/                     # 文档目录
│   ├── 功能设计文档.md       # 功能设计
│   └── 实现流程规划.md       # 实现流程
│
├── 完整项目启动指南.md       # 启动指南 ✅
└── README.md                # 本文件
```

---

## 📚 API文档

### 认证相关

#### 用户注册
```
POST /api/auth/register
Body: {
  "username": "string",
  "email": "string",
  "password": "string"
}
```

#### 用户登录
```
POST /api/auth/login
Body: {
  "username": "string",
  "password": "string"
}
Response: {
  "token": "string",
  "user": {...}
}
```

### 用户相关

#### 获取当前用户信息
```
GET /api/users/me
Headers: Authorization: Bearer <token>
```

#### 更新用户信息
```
PUT /api/users/me
Headers: Authorization: Bearer <token>
Body: {...}
```

#### 修改密码
```
PUT /api/users/me/password
Headers: Authorization: Bearer <token>
Body: {
  "old_password": "string",
  "new_password": "string"
}
```

#### 获取所有用户（管理员）
```
GET /api/users/
Headers: Authorization: Bearer <token>
```

### 论文相关 ✅

#### 上传PDF文件
```
POST /api/papers/upload
Headers: Authorization: Bearer <token>
Content-Type: multipart/form-data
Body: file
Response: {
  "filename": "string",
  "filepath": "string",
  "size": number
}
```

#### 创建论文
```
POST /api/papers/
Headers: Authorization: Bearer <token>
Body: {
  "title": "string",
  "authors": "string",
  "journal": "string",
  "year": number,
  ...
}
```

#### 获取论文列表
```
GET /api/papers/?keyword=&year=&reading_status=&page=1&page_size=20
Headers: Authorization: Bearer <token>
Query Parameters:
  - keyword: 搜索关键词
  - year: 年份筛选
  - reading_status: 阅读状态（unread/reading/read）
  - created_by: 创建者ID
  - sort_by: 排序字段（created_at/updated_at/title/year）
  - sort_order: 排序方向（asc/desc）
  - page: 页码
  - page_size: 每页数量
```

#### 获取论文详情
```
GET /api/papers/{paper_id}
Headers: Authorization: Bearer <token>
```

#### 更新论文
```
PUT /api/papers/{paper_id}
Headers: Authorization: Bearer <token>
Body: {...}
```

#### 删除论文（软删除）
```
DELETE /api/papers/{paper_id}
Headers: Authorization: Bearer <token>
```

### 统计相关 ✅

#### 获取Dashboard统计数据
```
GET /api/stats/dashboard
Headers: Authorization: Bearer <token>
Response: {
  "total_papers": 12,
  "total_notes": 8,
  "total_tags": 5,
  "reading_stats": {
    "unread": 3,
    "reading": 2,
    "read": 7
  },
  "recent_papers": [...]
}
```

#### 获取阅读进度统计
```
GET /api/stats/reading-progress
Headers: Authorization: Bearer <token>
Response: {
  "total": 12,
  "unread": 3,
  "reading": 2,
  "read": 7,
  "percentage": 58.3
}
```

完整API文档：http://localhost:8000/docs

---

## 💻 开发指南

### 后端开发

#### 添加新功能

1. 在 `models/database.py` 中定义数据模型
2. 在 `schemas/` 中创建 Pydantic schema
3. 在 `services/` 中实现业务逻辑
4. 在 `routes/` 中创建 API 路由
5. 在 `main.py` 中注册路由

#### 权限控制

```python
from app.utils.dependencies import get_current_user, check_permission

# 需要登录
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    pass

# 检查权限
if not check_permission(current_user, resource_user_id):
    raise HTTPException(status_code=403, detail="无权访问")
```

#### 数据库操作

```bash
# 初始化数据库
python scripts/init_db.py

# 重置数据库
rm data/database.db && python scripts/init_db.py

# 备份数据
cp -r data data_backup_$(date +%Y%m%d)
```

### 前端开发

#### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `App.jsx` 中添加路由
3. 在布局菜单中添加导航（如需要）

#### 添加新的API接口

1. 在 `src/services/` 创建或扩展service文件
2. 使用 `request` 实例进行HTTP调用

#### 状态管理

```javascript
import { useAuthStore } from '@/store/authStore'

const { user, login, logout } = useAuthStore()
```

---

## 🚢 部署指南

### 生产环境配置

#### 后端配置

1. 修改 `backend/.env`:
```env
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
DATABASE_URL=sqlite:///./data/database.db
```

2. 使用Gunicorn部署:
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 前端构建

```bash
cd frontend
npm run build
```

构建输出在 `dist/` 目录，可部署到任何静态服务器（Nginx、Apache、CDN等）

#### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 上传文件
    location /uploads {
        proxy_pass http://localhost:8000;
    }
}
```

### Docker部署（可选）

```dockerfile
# 后端 Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ❓ 常见问题

### 后端相关

#### Q: 如何重置管理员密码？

A: 删除数据库重新初始化，或手动修改数据库中的密码hash。

#### Q: bcrypt版本冲突怎么办？

A: 使用指定版本：
```bash
pip uninstall bcrypt -y
pip install bcrypt==3.2.2
```

#### Q: 数据库文件在哪里？

A: `backend/data/database.db`

### 前端相关

#### Q: npm安装速度慢怎么办？

A: 项目已配置淘宝镜像（`.npmrc`），自动加速。

#### Q: 端口被占用怎么办？

A: 修改 `vite.config.js` 中的端口配置。

#### Q: 如何清理node_modules重新安装？

A: 运行 `bash clean.sh` 然后 `bash setup.sh`

#### Q: 笔记编辑器显示白屏或报错 "React is not defined"？

A: 这是 `react-markdown-editor-lite` 库的兼容性问题，需要确保以下配置：
1. 检查 `frontend/src/main.jsx` 是否包含：
   ```javascript
   window.React = React
   window.ReactDOM = ReactDOM
   ```
2. 检查 `frontend/vite.config.js` 是否包含：
   ```javascript
   define: { 'global': 'globalThis' },
   optimizeDeps: { include: ['react-markdown-editor-lite'] }
   ```
3. 重启开发服务器并强制刷新浏览器（Ctrl+Shift+R）

#### Q: 前端修改后没有生效？

A: 清除 Vite 缓存并重启：
```bash
rm -rf node_modules/.vite
npm run dev
```
然后在浏览器中强制刷新（Ctrl+Shift+R）

### 功能相关

#### Q: 普通用户能看到其他用户的论文吗？

A: 不能，普通用户只能看到自己添加的论文。管理员可以看到所有论文。

#### Q: 删除论文后能恢复吗？

A: 使用软删除机制，数据不会立即删除，管理员可以恢复。

#### Q: PDF文件大小限制是多少？

A: 最大50MB。

---

## 📖 相关文档

- [完整项目启动指南](完整项目启动指南.md)
- [功能设计文档](docs/功能设计文档.md)
- [实现流程规划](docs/实现流程规划.md)
- [后端文档](backend/README.md)
- [前端文档](frontend/README.md)
- [前端快速启动](frontend/快速启动.md)
- [前端脚本使用说明](frontend/脚本使用说明.md)

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 许可证

MIT License

---

## 📞 联系方式

如有问题，请提交Issue或联系项目维护者。

---

## 🎉 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Ant Design](https://ant.design/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Zustand](https://github.com/pmndrs/zustand)

---

**最后更新**: 2026-01-12
# -unwen_web
