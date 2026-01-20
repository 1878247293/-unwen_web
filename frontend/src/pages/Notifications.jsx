import React, { useState, useEffect } from 'react'
import { List, Card, Badge, Button, Empty, message, Tag, Avatar, Space, Pagination, Tabs, Modal } from 'antd'
import { BellOutlined, CheckOutlined, DeleteOutlined, UserOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import notificationService from '../services/notificationService'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const Notifications = () => {
  const navigate = useNavigate()
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [unreadCount, setUnreadCount] = useState(0)
  const [activeTab, setActiveTab] = useState('all') // all, unread, read

  // 加载通知列表
  const loadNotifications = async () => {
    setLoading(true)
    try {
      const params = {
        page,
        page_size: pageSize
      }

      // 根据标签页筛选
      if (activeTab === 'unread') {
        params.is_read = false
      } else if (activeTab === 'read') {
        params.is_read = true
      }

      const response = await notificationService.getNotifications(params)
      if (response.code === 200) {
        setNotifications(response.data.notifications || [])
        setTotal(response.data.total || 0)
      }
    } catch (error) {
      message.error('获取通知列表失败')
    } finally {
      setLoading(false)
    }
  }

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

  useEffect(() => {
    loadNotifications()
    loadUnreadCount()
  }, [page, pageSize, activeTab])

  // 标记为已读
  const handleMarkAsRead = async (notificationId) => {
    try {
      const response = await notificationService.markAsRead(notificationId)
      if (response.code === 200) {
        message.success('已标记为已读')
        loadNotifications()
        loadUnreadCount()
      }
    } catch (error) {
      message.error('操作失败')
    }
  }

  // 标记全部为已读
  const handleMarkAllAsRead = async () => {
    if (unreadCount === 0) {
      message.info('没有未读通知')
      return
    }

    try {
      const response = await notificationService.markAllAsRead()
      if (response.code === 200) {
        message.success('所有通知已标记为已读')
        loadNotifications()
        loadUnreadCount()
      }
    } catch (error) {
      message.error('操作失败')
    }
  }

  // 删除通知
  const handleDelete = (notificationId) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这条通知吗？',
      okType: 'danger',
      onOk: async () => {
        try {
          const response = await notificationService.deleteNotification(notificationId)
          if (response.code === 200) {
            message.success('通知删除成功')
            loadNotifications()
            loadUnreadCount()
          }
        } catch (error) {
          message.error('删除失败')
        }
      }
    })
  }

  // 点击通知
  const handleNotificationClick = async (notification) => {
    // 如果未读，先标记为已读
    if (!notification.is_read) {
      await handleMarkAsRead(notification.id)
    }

    // 跳转到相关页面
    if (notification.link) {
      navigate(notification.link)
    }
  }

  // 获取通知类型标签
  const getTypeTag = (type) => {
    const typeMap = {
      comment_reply: { color: 'blue', text: '评论回复' },
      system: { color: 'green', text: '系统通知' },
      mention: { color: 'orange', text: '提及' }
    }
    const config = typeMap[type] || { color: 'default', text: '通知' }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const tabItems = [
    {
      key: 'all',
      label: `全部通知 (${total})`
    },
    {
      key: 'unread',
      label: (
        <Badge count={unreadCount} offset={[10, 0]}>
          未读通知
        </Badge>
      )
    },
    {
      key: 'read',
      label: '已读通知'
    }
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <BellOutlined style={{ fontSize: '20px' }} />
            <span style={{ fontSize: '20px', fontWeight: 'bold' }}>通知中心</span>
            {unreadCount > 0 && (
              <Badge count={unreadCount} style={{ backgroundColor: '#52c41a' }} />
            )}
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<CheckOutlined />}
            onClick={handleMarkAllAsRead}
            disabled={unreadCount === 0}
          >
            全部已读
          </Button>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
        />

        <List
          loading={loading}
          dataSource={notifications}
          locale={{
            emptyText: (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="暂无通知"
              />
            )
          }}
          renderItem={(notification) => (
            <List.Item
              key={notification.id}
              style={{
                backgroundColor: notification.is_read ? '#fff' : '#f0f7ff',
                padding: '16px',
                marginBottom: '8px',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s',
                border: notification.is_read ? '1px solid #f0f0f0' : '1px solid #91d5ff'
              }}
              actions={[
                !notification.is_read && (
                  <Button
                    type="link"
                    size="small"
                    icon={<CheckOutlined />}
                    onClick={(e) => {
                      e.stopPropagation()
                      handleMarkAsRead(notification.id)
                    }}
                  >
                    标记已读
                  </Button>
                ),
                <Button
                  type="link"
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(notification.id)
                  }}
                >
                  删除
                </Button>
              ].filter(Boolean)}
              onClick={() => handleNotificationClick(notification)}
            >
              <List.Item.Meta
                avatar={
                  notification.sender_avatar ? (
                    <Avatar src={notification.sender_avatar} />
                  ) : (
                    <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
                  )
                }
                title={
                  <Space>
                    {getTypeTag(notification.type)}
                    <span style={{ fontWeight: notification.is_read ? 'normal' : 'bold' }}>
                      {notification.title}
                    </span>
                    {!notification.is_read && (
                      <Badge status="processing" />
                    )}
                  </Space>
                }
                description={
                  <div>
                    <div style={{ marginBottom: '8px', color: '#595959' }}>
                      {notification.content}
                    </div>
                    <Space split="|" style={{ fontSize: '12px', color: '#999' }}>
                      {notification.sender_username && (
                        <span>来自: {notification.sender_username}</span>
                      )}
                      <span>{dayjs(notification.created_at).fromNow()}</span>
                    </Space>
                  </div>
                }
              />
            </List.Item>
          )}
        />

        {total > pageSize && (
          <div style={{ marginTop: '16px', textAlign: 'right' }}>
            <Pagination
              current={page}
              pageSize={pageSize}
              total={total}
              onChange={(newPage, newPageSize) => {
                setPage(newPage)
                setPageSize(newPageSize)
              }}
              showSizeChanger
              showTotal={(total) => `共 ${total} 条`}
            />
          </div>
        )}
      </Card>
    </div>
  )
}

export default Notifications
