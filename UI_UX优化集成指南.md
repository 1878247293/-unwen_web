# UI/UX优化功能集成指南

**实现日期**: 2026-01-12
**版本**: v1.5.0

---

## 📋 目录

1. [功能概览](#功能概览)
2. [Skeleton骨架屏](#skeleton骨架屏)
3. [响应式布局](#响应式布局)
4. [页面切换动画](#页面切换动画)
5. [快捷键系统](#快捷键系统)
6. [用户引导Tour](#用户引导tour)
7. [集成步骤](#集成步骤)
8. [使用示例](#使用示例)

---

## 🎯 功能概览

本次UI/UX优化实现了以下5个核心功能：

| 功能 | 文件路径 | 描述 |
|------|---------|------|
| ✅ Skeleton骨架屏 | `/frontend/src/components/Skeleton.jsx` | 加载占位符，提升加载体验 |
| ✅ 响应式布局 | `/frontend/src/styles/responsive.css` | 移动端适配，多设备支持 |
| ✅ 页面切换动画 | `/frontend/src/components/PageTransition.jsx` | 平滑的页面过渡效果 |
| ✅ 快捷键系统 | `/frontend/src/hooks/useHotkeys.jsx` | 键盘快捷键支持 |
| ✅ 用户引导Tour | `/frontend/src/components/UserTour.jsx` | 新用户功能引导 |

---

## 🦴 Skeleton骨架屏

### 组件说明

Skeleton组件用于在内容加载时显示占位符，改善用户等待体验。

### 基础使用

```jsx
import Skeleton, {
  PaperListSkeleton,
  PaperDetailSkeleton,
  CardSkeleton,
  TableSkeleton
} from '@/components/Skeleton'

// 基础骨架屏
<Skeleton type="text" />
<Skeleton type="title" width="60%" />
<Skeleton type="avatar" />
<Skeleton type="image" height={200} />
<Skeleton type="button" width={100} />

// 重复骨架屏
<Skeleton type="text" count={5} />

// 预定义组合
<PaperListSkeleton count={3} />
<PaperDetailSkeleton />
<CardSkeleton count={4} />
<TableSkeleton rows={5} columns={4} />
```

### 在页面中使用

```jsx
// Papers.jsx示例
import { PaperListSkeleton } from '@/components/Skeleton'

const Papers = () => {
  const [loading, setLoading] = useState(true)
  const [papers, setPapers] = useState([])

  return (
    <div>
      {loading ? (
        <PaperListSkeleton count={5} />
      ) : (
        <Table dataSource={papers} />
      )}
    </div>
  )
}
```

### 支持的类型

- `text` - 文本行
- `title` - 标题
- `avatar` - 头像
- `image` - 图片
- `button` - 按钮
- `card` - 卡片

---

## 📱 响应式布局

### 样式说明

响应式CSS提供了全局的移动端适配，无需额外配置。

### 断点定义

```css
/* xs: < 576px   手机竖屏 */
/* sm: 576-768px 手机横屏/小平板 */
/* md: 768-992px 平板 */
/* lg: 992-1200px 小桌面 */
/* xl: 1200-1600px 桌面 */
/* xxl: > 1600px 大屏 */
```

### 集成方式

在 `main.jsx` 或 `App.jsx` 中引入：

```jsx
import '@/styles/responsive.css'
```

### 主要优化

1. **移动端基础优化**
   - 字体大小调整（14px）
   - 容器内边距优化
   - 表格横向滚动
   - 模态框自适应

2. **布局响应式**
   - 侧边栏在移动端改为抽屉
   - Header内容自适应
   - 表格在移动端转为卡片布局

3. **表单优化**
   - 标签左对齐
   - 双列改单列
   - 按钮全宽显示

4. **触摸优化**
   - 点击区域增大（44px）
   - 禁用hover，使用active
   - 表单控件加大

### 自定义类名

```html
<!-- 打印时隐藏 -->
<button className="no-print">操作按钮</button>

<!-- 桌面端隐藏 -->
<div className="papers-mobile-cards">
  <!-- 移动端卡片视图 -->
</div>
```

---

## 🎬 页面切换动画

### 组件说明

PageTransition组件为页面切换添加平滑过渡效果。

### 安装依赖

```bash
npm install react-transition-group
```

### 基础使用

在路由层级使用PageTransition：

```jsx
import PageTransition from '@/components/PageTransition'
import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <PageTransition mode="fade">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/papers" element={<Papers />} />
        {/* ... */}
      </Routes>
    </PageTransition>
  )
}
```

### 动画模式

支持5种过渡效果：

- `fade` - 淡入淡出（默认）
- `slide-left` - 从右滑入
- `slide-right` - 从左滑入
- `slide-up` - 从下滑入
- `zoom` - 缩放效果

```jsx
<PageTransition mode="slide-left" timeout={300}>
  {children}
</PageTransition>
```

### 注意事项

- 在Layout组件的Outlet位置使用
- 不要在每个页面组件中单独使用
- 移动端会自动减弱动画效果以提升性能

---

## ⌨️ 快捷键系统

### Hook说明

useHotkeys提供全局快捷键支持，提升操作效率。

### 基础使用

在根组件中注册快捷键：

```jsx
import useHotkeys, { ShortcutsHelp } from '@/hooks/useHotkeys'

function App() {
  useHotkeys()  // 注册快捷键

  return (
    <>
      <Routes>...</Routes>
      <ShortcutsHelp />  {/* 快捷键帮助模态框 */}
    </>
  )
}
```

### 支持的快捷键

| 快捷键 | 功能 | 描述 |
|--------|------|------|
| `Ctrl+K` / `⌘+K` | 全局搜索 | 聚焦搜索框 |
| `Ctrl+N` / `⌘+N` | 新建论文 | 跳转到添加论文页 |
| `Ctrl+H` / `⌘+H` | 返回首页 | 跳转到Dashboard |
| `Ctrl+P` / `⌘+P` | 论文列表 | 跳转到论文列表 |
| `Ctrl+T` / `⌘+T` | 标签管理 | 跳转到标签页面 |
| `Shift+/` | 快捷键帮助 | 显示帮助面板 |

### 搜索框集成

为搜索框添加快捷键提示：

```jsx
<Input
  className="global-search-input"
  placeholder="搜索论文..."
  suffix={
    <span className="global-search-shortcut-hint">
      <span className="shortcut-key">Ctrl</span>
      <span>+</span>
      <span className="shortcut-key">K</span>
    </span>
  }
/>
```

### 自定义快捷键

修改 `useHotkeys.jsx` 中的 `SHORTCUTS` 配置：

```javascript
const SHORTCUTS = {
  MY_SHORTCUT: {
    key: 'm',
    ctrl: true,
    description: '我的功能'
  },
}
```

添加对应的处理逻辑：

```javascript
if ((ctrlKey || metaKey) && key.toLowerCase() === 'm') {
  event.preventDefault()
  // 执行操作
}
```

---

## 🎯 用户引导Tour

### 组件说明

UserTour为新用户提供交互式功能引导，改善首次使用体验。

### 基础使用

在Layout或App组件中添加：

```jsx
import { UserTour, TriggerTourButton } from '@/components/UserTour'

function Layout() {
  return (
    <>
      <Header />
      <Content>
        <Outlet />
      </Content>
      <UserTour />  {/* 自动检测新用户 */}
      <TriggerTourButton />  {/* 手动触发按钮 */}
    </>
  )
}
```

### 引导步骤配置

在 `UserTour.jsx` 中为不同页面配置引导步骤：

```javascript
const dashboardSteps = [
  {
    title: '欢迎 🎉',
    description: '让我们快速了解功能吧！',
    target: null,  // 居中显示
  },
  {
    title: '统计数据',
    description: '查看您的研究进度',
    target: () => document.querySelector('.dashboard-stats'),
  },
]
```

### 自定义引导

为新页面添加引导步骤：

```javascript
// 1. 定义步骤
const myPageSteps = [
  {
    title: '标题',
    description: '描述',
    target: () => document.querySelector('.my-element'),
  },
]

// 2. 在useEffect中添加路由判断
else if (path === '/my-page') {
  tourSteps = myPageSteps
}
```

### 重置引导状态

```javascript
import { resetTourStatus } from '@/components/UserTour'

// 清除"已查看"标记
resetTourStatus()
```

### 检测新用户

组件会检查 `localStorage` 中的 `has-seen-tour` 标记：
- 首次访问：自动显示引导
- 已访问过：不显示引导
- 点击"?"按钮：重新触发引导

---

## 🔧 集成步骤

### 1. 引入响应式样式

在 `main.jsx` 中添加：

```jsx
import './styles/responsive.css'
```

### 2. 添加页面切换动画

修改 `App.jsx`：

```jsx
import PageTransition from './components/PageTransition'

function App() {
  return (
    <PageTransition mode="fade">
      <Routes>
        {/* 路由配置 */}
      </Routes>
    </PageTransition>
  )
}
```

### 3. 注册快捷键

在 `App.jsx` 中：

```jsx
import useHotkeys, { ShortcutsHelp } from './hooks/useHotkeys'

function App() {
  useHotkeys()

  return (
    <>
      <Routes>...</Routes>
      <ShortcutsHelp />
    </>
  )
}
```

### 4. 添加用户引导

在 `Layout.jsx` 中：

```jsx
import { UserTour, TriggerTourButton } from './components/UserTour'

function Layout() {
  return (
    <>
      {/* 布局内容 */}
      <UserTour />
      <TriggerTourButton />
    </>
  )
}
```

### 5. 使用Skeleton

在需要加载状态的页面中：

```jsx
import { PaperListSkeleton } from './components/Skeleton'

{loading ? <PaperListSkeleton /> : <Table dataSource={data} />}
```

---

## 💡 使用示例

### 示例1: 论文列表页完整集成

```jsx
import React, { useState, useEffect } from 'react'
import { Table, Input } from 'antd'
import { PaperListSkeleton } from '@/components/Skeleton'

const Papers = () => {
  const [loading, setLoading] = useState(true)
  const [papers, setPapers] = useState([])

  useEffect(() => {
    fetchPapers()
  }, [])

  const fetchPapers = async () => {
    setLoading(true)
    try {
      const data = await paperService.getPapers()
      setPapers(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {/* 搜索框（带快捷键提示） */}
      <Input
        className="global-search-input"
        placeholder="搜索论文... (Ctrl+K)"
      />

      {/* 加载状态 */}
      {loading ? (
        <PaperListSkeleton count={5} />
      ) : (
        <Table dataSource={papers} />
      )}
    </div>
  )
}

export default Papers
```

### 示例2: 响应式卡片列表

```jsx
<div className="papers-list-container">
  {/* 桌面端：表格 */}
  <Table
    dataSource={papers}
    columns={columns}
    className="desktop-table"
  />

  {/* 移动端：卡片 */}
  <div className="papers-mobile-cards">
    {papers.map(paper => (
      <div key={paper.id} className="paper-mobile-card">
        <div className="paper-mobile-card-title">{paper.title}</div>
        <div className="paper-mobile-card-meta">
          <span>{paper.authors}</span>
          <span>{paper.year}</span>
        </div>
        <div className="paper-mobile-card-actions">
          <Button>查看</Button>
          <Button>编辑</Button>
        </div>
      </div>
    ))}
  </div>
</div>
```

### 示例3: 自定义页面引导

```jsx
// 在UserTour.jsx中添加
const settingsSteps = [
  {
    title: '个人设置',
    description: '管理您的账号信息和偏好设置',
    target: null,
  },
  {
    title: '基本信息',
    description: '更新您的用户名、邮箱等信息',
    target: () => document.querySelector('.settings-basic'),
  },
  {
    title: '修改密码',
    description: '定期修改密码以保护账号安全',
    target: () => document.querySelector('.settings-password'),
  },
]

// 在useEffect中添加
else if (path === '/settings') {
  tourSteps = settingsSteps
}
```

---

## 📝 注意事项

### 1. 性能优化

- Skeleton动画在移动端自动简化
- 页面切换动画支持`prefers-reduced-motion`
- 响应式布局使用CSS而非JS判断

### 2. 兼容性

- 快捷键在Mac上自动使用⌘代替Ctrl
- 触摸设备优化：增大点击区域
- 打印适配：自动隐藏交互元素

### 3. 可访问性

- 快捷键不影响屏幕阅读器
- Focus样式明显
- 颜色对比度符合WCAG标准

### 4. 调试技巧

```javascript
// 重置Tour状态
localStorage.removeItem('has-seen-tour')

// 禁用页面切换动画
// 在PageTransition.css中设置
transition: none !important;

// 查看当前断点
console.log(window.innerWidth)
```

---

## 🔄 版本历史

### v1.5.0 (2026-01-12)

- ✅ 新增Skeleton骨架屏组件（5种类型）
- ✅ 新增响应式布局CSS（6个断点）
- ✅ 新增页面切换动画（5种模式）
- ✅ 新增快捷键系统（6个快捷键）
- ✅ 新增用户引导Tour（4个页面引导）

---

## 📚 相关文档

- [Ant Design Tour](https://ant.design/components/tour-cn)
- [React Transition Group](https://reactcommunity.org/react-transition-group/)
- [响应式设计断点](https://ant.design/docs/spec/layout-cn#Breakpoint)

---

**维护者**: Claude (Sonnet 4.5)
**最后更新**: 2026-01-12
