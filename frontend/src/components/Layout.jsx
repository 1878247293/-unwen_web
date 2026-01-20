import { useState, useEffect } from 'react'
import { Layout as AntLayout, Menu, Avatar, Dropdown, Badge } from 'antd'
import {
  HomeOutlined,
  FileTextOutlined,
  TagOutlined,
  UserOutlined,
  LogoutOutlined,
  DashboardOutlined,
  TeamOutlined,
  BulbOutlined,
  BellOutlined,
  FormOutlined,
  GlobalOutlined,
  CommentOutlined,
  MonitorOutlined,
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import notificationService from '../services/notificationService'
import usePreloadRoutes from '../hooks/usePreloadRoutes'
import BackgroundDecoration from './BackgroundDecoration'
import './Layout.css'

const { Header, Content, Sider } = AntLayout

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const [collapsed, setCollapsed] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)

  // 预加载常用路由
  usePreloadRoutes()

  // 加载未读通知数量
  const loadUnreadCount = async () => {
    try {
      const response = await notificationService.getUnreadCount()
      if (response.code === 200) {
        setUnreadCount(response.data.unread_count || 0)
      }
    } catch (error) {
      console.error('获取未读通知数量失败', error)
    }
  }

  // 初始加载和定期刷新未读通知数量
  useEffect(() => {
    loadUnreadCount()

    // 优化：每60秒刷新一次（原来是30秒），减少API请求频率
    const interval = setInterval(() => {
      loadUnreadCount()
    }, 60000)

    return () => clearInterval(interval)
  }, [])

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '仪表盘',
    },
    {
      key: '/papers',
      icon: <FileTextOutlined />,
      label: '论文库',
    },
    {
      key: '/tags',
      icon: <TagOutlined />,
      label: '标签管理',
    },
    {
      key: '/ideas',
      icon: <FormOutlined />,
      label: '想法收集',
    },
    {
      key: '/websites',
      icon: <GlobalOutlined />,
      label: '网站收藏',
    },
    {
      key: '/community',
      icon: <CommentOutlined />,
      label: '交流广场',
    },
    {
      key: '/suggestions',
      icon: <BulbOutlined />,
      label: '改进建议',
    },
    // 管理员菜单
    ...(user?.role === 'admin' ? [
      {
        type: 'divider',
      },
      {
        key: '/admin/dashboard',
        icon: <DashboardOutlined />,
        label: '管理员控制台',
      },
      {
        key: '/admin/users',
        icon: <TeamOutlined />,
        label: '用户管理',
      },
      {
        key: '/admin/system',
        icon: <MonitorOutlined />,
        label: '资源监控',
      },
    ] : []),
  ]

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  const handleUserMenuClick = ({ key }) => {
    if (key === 'logout') {
      logout()
      navigate('/login')
    } else if (key === 'profile') {
      navigate('/profile')
    }
  }

  return (
    <>
      {/* 背景装饰 */}
      <BackgroundDecoration />

      <AntLayout style={{ minHeight: '100vh', position: 'relative' }}>
        <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
          <div className="logo">
            <h2>{collapsed ? '论文' : '科研论文管理'}</h2>
          </div>
          <Menu
            theme="dark"
            selectedKeys={[location.pathname]}
            mode="inline"
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>

        <AntLayout>
          <Header className="site-layout-header">
            <div className="header-right">
              {/* 通知铃铛 */}
              <Badge count={unreadCount} offset={[0, 8]}>
                <BellOutlined
                  style={{
                    fontSize: '20px',
                    cursor: 'pointer',
                    marginRight: '24px',
                    color: unreadCount > 0 ? '#1890ff' : '#666'
                  }}
                  onClick={() => {
                    navigate('/notifications')
                    // 刷新未读数量
                    setTimeout(() => loadUnreadCount(), 1000)
                  }}
                />
              </Badge>

              {/* 用户下拉菜单 */}
              <Dropdown
                menu={{
                  items: userMenuItems,
                  onClick: handleUserMenuClick,
                }}
              >
                <div className="user-info">
                  <Avatar icon={<UserOutlined />} src={user?.avatar} />
                  <span className="username">{user?.username}</span>
                </div>
              </Dropdown>
            </div>
          </Header>

          <Content className="site-layout-content">
            <div className="content-wrapper">
              <Outlet />
            </div>
          </Content>
        </AntLayout>
      </AntLayout>
    </>
  )
}
