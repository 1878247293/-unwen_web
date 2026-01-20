import { useState, useEffect } from 'react'
import {
  Card,
  Tabs,
  Switch,
  Space,
  Typography,
  Table,
  Button,
  message,
  Tag,
  Modal
} from 'antd'
import {
  CommentOutlined,
  StarOutlined,
  WarningOutlined,
  EyeInvisibleOutlined,
  SettingOutlined
} from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import DiscussionInput from '../components/DiscussionInput'
import DiscussionList from '../components/DiscussionList'
import discussionService from '../services/discussionService'
import dayjs from 'dayjs'

const { Title } = Typography

const Community = () => {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('all')
  const [allowAnonymous, setAllowAnonymous] = useState(false)
  const [loadingSettings, setLoadingSettings] = useState(false)
  const [reports, setReports] = useState([])
  const [loadingReports, setLoadingReports] = useState(false)
  const [reportsPage, setReportsPage] = useState(1)
  const [reportsPageSize, setReportsPageSize] = useState(10)
  const [reportsTotal, setReportsTotal] = useState(0)
  const [favorites, setFavorites] = useState([])
  const [loadingFavorites, setLoadingFavorites] = useState(false)
  const [favoritesPage, setFavoritesPage] = useState(1)
  const [favoritesPageSize, setFavoritesPageSize] = useState(10)
  const [favoritesTotal, setFavoritesTotal] = useState(0)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const isAdmin = user?.role === 'admin'

  // 加载匿名设置
  const loadAnonymousSetting = async () => {
    try {
      const response = await discussionService.getAnonymousSetting()
      if (response.code === 200) {
        setAllowAnonymous(response.data.allow_anonymous)
      }
    } catch (error) {
      console.error('Failed to load anonymous setting:', error)
    }
  }

  // 更新匿名设置
  const handleAnonymousSettingChange = async (checked) => {
    setLoadingSettings(true)
    try {
      const response = await discussionService.updateAnonymousSetting(checked)
      if (response.code === 200) {
        setAllowAnonymous(checked)
        message.success('设置已更新')
      } else {
        message.error(response.message || '更新失败')
      }
    } catch (error) {
      message.error('更新失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoadingSettings(false)
    }
  }

  // 加载举报列表
  const loadReports = async () => {
    setLoadingReports(true)
    try {
      const response = await discussionService.getReports({
        page: reportsPage,
        page_size: reportsPageSize,
        status: 'pending'
      })
      if (response.code === 200) {
        setReports(response.data.reports || [])
        setReportsTotal(response.data.total || 0)
      }
    } catch (error) {
      message.error('加载举报列表失败')
    } finally {
      setLoadingReports(false)
    }
  }

  // 处理举报
  const handleReport = async (reportId, status) => {
    try {
      const response = await discussionService.handleReport(reportId, { status })
      if (response.code === 200) {
        message.success(status === 'handled' ? '已处理举报' : '已驳回举报')
        loadReports()
      } else {
        message.error(response.message || '操作失败')
      }
    } catch (error) {
      message.error('操作失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  // 加载收藏列表
  const loadFavorites = async () => {
    setLoadingFavorites(true)
    try {
      const response = await discussionService.getFavorites({
        page: favoritesPage,
        page_size: favoritesPageSize
      })
      if (response.code === 200) {
        setFavorites(response.data.discussions || [])
        setFavoritesTotal(response.data.total || 0)
      }
    } catch (error) {
      message.error('加载收藏列表失败')
    } finally {
      setLoadingFavorites(false)
    }
  }

  useEffect(() => {
    if (isAdmin) {
      loadAnonymousSetting()
    }
  }, [isAdmin])

  useEffect(() => {
    if (activeTab === 'reports' && isAdmin) {
      loadReports()
    }
  }, [activeTab, reportsPage, reportsPageSize, isAdmin])

  useEffect(() => {
    if (activeTab === 'favorites') {
      loadFavorites()
    }
  }, [activeTab, favoritesPage, favoritesPageSize])

  // 处理讨论添加成功
  const handleDiscussionAdded = () => {
    setRefreshTrigger((prev) => prev + 1)
  }

  // 举报表格列
  const reportColumns = [
    {
      title: '讨论内容',
      dataIndex: ['discussion', 'content'],
      key: 'content',
      ellipsis: true,
      render: (text) => (
        <div style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {text}
        </div>
      )
    },
    {
      title: '举报原因',
      dataIndex: 'reason',
      key: 'reason',
      width: 200
    },
    {
      title: '举报人',
      dataIndex: ['reporter', 'username'],
      key: 'reporter',
      width: 120
    },
    {
      title: '举报时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const statusMap = {
          pending: { text: '待处理', color: 'orange' },
          handled: { text: '已处理', color: 'green' },
          rejected: { text: '已驳回', color: 'red' }
        }
        const s = statusMap[status] || statusMap.pending
        return <Tag color={s.color}>{s.text}</Tag>
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            onClick={() => handleReport(record.id, 'handled')}
          >
            处理
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => handleReport(record.id, 'rejected')}
          >
            驳回
          </Button>
        </Space>
      )
    }
  ]

  // 标签页配置
  const tabItems = [
    {
      key: 'all',
      label: (
        <span>
          <CommentOutlined />
          全部讨论
        </span>
      ),
      children: (
        <div>
          <div style={{ marginBottom: '24px' }}>
            <DiscussionInput onDiscussionAdded={handleDiscussionAdded} />
          </div>
          <DiscussionList key={`all-${refreshTrigger}`} showHidden={false} />
        </div>
      )
    },
    {
      key: 'favorites',
      label: (
        <span>
          <StarOutlined />
          我的收藏
        </span>
      ),
      children: (
        <div>
          {favorites.length === 0 ? (
            <Card>
              <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                暂无收藏的讨论
              </div>
            </Card>
          ) : (
            <Card>
              {favorites.map((discussion) => (
                <div
                  key={discussion.id}
                  style={{
                    padding: '16px',
                    borderBottom: '1px solid #f0f0f0',
                    cursor: 'pointer'
                  }}
                  onClick={() => {
                    setActiveTab('all')
                  }}
                >
                  <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                    {discussion.is_anonymous ? '匿名用户' : discussion.user?.username}
                    <span style={{ marginLeft: '8px', fontSize: '12px', color: '#999' }}>
                      {dayjs(discussion.created_at).format('YYYY-MM-DD HH:mm')}
                    </span>
                  </div>
                  <div style={{ color: '#666', whiteSpace: 'pre-wrap' }}>
                    {discussion.content}
                  </div>
                </div>
              ))}
              {favoritesTotal > favoritesPageSize && (
                <div style={{ marginTop: '16px', textAlign: 'center' }}>
                  <Button
                    onClick={() => setFavoritesPage((prev) => prev + 1)}
                    loading={loadingFavorites}
                  >
                    加载更多
                  </Button>
                </div>
              )}
            </Card>
          )}
        </div>
      )
    }
  ]

  // 管理员专属标签页
  if (isAdmin) {
    tabItems.push(
      {
        key: 'reports',
        label: (
          <span>
            <WarningOutlined />
            举报管理
          </span>
        ),
        children: (
          <Card>
            <Table
              columns={reportColumns}
              dataSource={reports}
              rowKey="id"
              loading={loadingReports}
              pagination={{
                current: reportsPage,
                pageSize: reportsPageSize,
                total: reportsTotal,
                onChange: (page, pageSize) => {
                  setReportsPage(page)
                  setReportsPageSize(pageSize)
                },
                showTotal: (total) => `共 ${total} 条举报`
              }}
            />
          </Card>
        )
      },
      {
        key: 'hidden',
        label: (
          <span>
            <EyeInvisibleOutlined />
            包含隐藏内容
          </span>
        ),
        children: (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <DiscussionInput onDiscussionAdded={handleDiscussionAdded} />
            </div>
            <DiscussionList key={`hidden-${refreshTrigger}`} showHidden={true} />
          </div>
        )
      }
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={2} style={{ margin: 0 }}>
            <CommentOutlined style={{ color: '#1890ff', marginRight: '12px' }} />
            交流广场
          </Title>
        </div>
      </Card>

      {/* 管理员设置面板 */}
      {isAdmin && (
        <Card style={{ marginBottom: '24px' }} title={<><SettingOutlined /> 管理员设置</>}>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '14px' }}>允许匿名发布讨论</span>
              <Switch
                checked={allowAnonymous}
                onChange={handleAnonymousSettingChange}
                loading={loadingSettings}
              />
            </div>
          </Space>
        </Card>
      )}

      {/* 标签页 */}
      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} />
      </Card>
    </div>
  )
}

export default Community
