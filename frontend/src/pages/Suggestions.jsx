import React, { useState, useEffect } from 'react'
import {
  Card,
  List,
  Checkbox,
  Input,
  Button,
  Space,
  message,
  Tag,
  Avatar,
  Popconfirm,
  Empty,
  Spin
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined
} from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import suggestionService from '../services/suggestionService'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const { TextArea } = Input

const Suggestions = () => {
  const { user } = useAuthStore()
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [newSuggestion, setNewSuggestion] = useState('')

  // 加载建议列表
  const loadSuggestions = async () => {
    setLoading(true)
    try {
      const response = await suggestionService.getSuggestions({
        page: 1,
        page_size: 1000 // 获取所有建议
      })

      if (response.code === 200) {
        setSuggestions(response.data.suggestions)
      } else {
        message.error(response.message || '加载建议列表失败')
      }
    } catch (error) {
      message.error('加载建议列表失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSuggestions()
  }, [])

  // 提交新建议 - 使用乐观更新
  const handleSubmit = async () => {
    if (!newSuggestion.trim()) {
      message.warning('请输入建议内容')
      return
    }

    setSubmitting(true)
    const content = newSuggestion.trim()

    try {
      const response = await suggestionService.createSuggestion(content)

      if (response.code === 200) {
        message.success('建议提交成功')
        setNewSuggestion('')

        // 乐观更新：将新建议添加到列表开头
        setSuggestions(prevSuggestions => [response.data, ...prevSuggestions])
      } else {
        message.error(response.message || '提交失败')
      }
    } catch (error) {
      message.error('提交失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSubmitting(false)
    }
  }

  // 切换完成状态（仅管理员）- 使用乐观更新
  const handleToggleComplete = async (suggestion) => {
    const isCompleting = suggestion.status === 'pending'
    const originalStatus = suggestion.status

    // 乐观更新：立即更新UI
    setSuggestions(prevSuggestions =>
      prevSuggestions.map(s =>
        s.id === suggestion.id
          ? {
              ...s,
              status: isCompleting ? 'completed' : 'pending',
              completed_at: isCompleting ? new Date().toISOString() : null,
              completed_by: isCompleting ? user?.id : null,
              completed_by_username: isCompleting ? user?.username : null
            }
          : s
      )
    )

    try {
      // 后台调用API
      const response = isCompleting
        ? await suggestionService.completeSuggestion(suggestion.id)
        : await suggestionService.uncompleteSuggestion(suggestion.id)

      if (response.code !== 200) {
        // API失败，回滚UI
        message.error(response.message || '操作失败')
        setSuggestions(prevSuggestions =>
          prevSuggestions.map(s =>
            s.id === suggestion.id ? { ...s, status: originalStatus } : s
          )
        )
      }
    } catch (error) {
      // 发生错误，回滚UI
      message.error('操作失败: ' + (error.response?.data?.detail || error.message))
      setSuggestions(prevSuggestions =>
        prevSuggestions.map(s =>
          s.id === suggestion.id ? { ...s, status: originalStatus } : s
        )
      )
    }
  }

  // 删除建议 - 使用乐观更新
  const handleDelete = async (suggestionId) => {
    // 保存原始列表，以便失败时恢复
    const originalSuggestions = [...suggestions]

    // 乐观更新：立即从列表中移除
    setSuggestions(prevSuggestions =>
      prevSuggestions.filter(s => s.id !== suggestionId)
    )

    try {
      const response = await suggestionService.deleteSuggestion(suggestionId)

      if (response.code !== 200) {
        // API失败，恢复原列表
        message.error(response.message || '删除失败')
        setSuggestions(originalSuggestions)
      } else {
        message.success('建议删除成功')
      }
    } catch (error) {
      // 发生错误，恢复原列表
      message.error('删除失败: ' + (error.response?.data?.detail || error.message))
      setSuggestions(originalSuggestions)
    }
  }

  // 统计数据
  const stats = {
    total: suggestions.length,
    pending: suggestions.filter(s => s.status === 'pending').length,
    completed: suggestions.filter(s => s.status === 'completed').length
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Card>
        <h1 style={{ marginBottom: '8px' }}>
          改进建议墙
        </h1>
        <p style={{ color: '#666', marginBottom: '24px' }}>
          欢迎提出你的改进建议和想法，让我们一起让系统变得更好！
        </p>

        {/* 统计信息 */}
        <div style={{ marginBottom: '24px' }}>
          <Space size="large">
            <span>
              <Tag color="blue">全部: {stats.total}</Tag>
            </span>
            <span>
              <Tag color="orange" icon={<ClockCircleOutlined />}>待处理: {stats.pending}</Tag>
            </span>
            <span>
              <Tag color="green" icon={<CheckCircleOutlined />}>已完成: {stats.completed}</Tag>
            </span>
          </Space>
        </div>

        {/* 添加新建议 */}
        <Card
          type="inner"
          title="提出新建议"
          style={{ marginBottom: '24px', background: '#fafafa' }}
        >
          <TextArea
            value={newSuggestion}
            onChange={(e) => setNewSuggestion(e.target.value)}
            placeholder="描述你的改进建议或想法..."
            autoSize={{ minRows: 3, maxRows: 6 }}
            maxLength={500}
            showCount
            style={{ marginBottom: '12px' }}
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleSubmit}
            loading={submitting}
          >
            提交建议
          </Button>
        </Card>

        {/* 建议列表 */}
        <Spin spinning={loading}>
          {suggestions.length === 0 ? (
            <Empty
              description="还没有建议，快来提出第一个吧！"
              style={{ marginTop: '40px' }}
            />
          ) : (
            <List
              dataSource={suggestions}
              renderItem={(item) => (
                <List.Item
                  key={item.id}
                  style={{
                    padding: '16px 0',
                    borderBottom: '1px solid #f0f0f0'
                  }}
                >
                  <div style={{ display: 'flex', width: '100%', gap: '16px' }}>
                    {/* 复选框（仅管理员可操作） */}
                    <div style={{ paddingTop: '4px' }}>
                      <Checkbox
                        checked={item.status === 'completed'}
                        onChange={() => handleToggleComplete(item)}
                        disabled={user?.role !== 'admin'}
                        style={{ fontSize: '18px' }}
                      />
                    </div>

                    {/* 内容区域 */}
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          fontSize: '15px',
                          lineHeight: '1.6',
                          color: item.status === 'completed' ? '#999' : '#000',
                          textDecoration: item.status === 'completed' ? 'line-through' : 'none',
                          marginBottom: '8px'
                        }}
                      >
                        {item.content}
                      </div>

                      <Space size="middle" wrap>
                        {/* 用户信息 */}
                        <Space size="small">
                          <Avatar
                            size="small"
                            src={item.avatar}
                            icon={<UserOutlined />}
                          />
                          <span style={{ fontSize: '13px', color: '#666' }}>
                            {item.username}
                          </span>
                        </Space>

                        {/* 创建时间 */}
                        <span style={{ fontSize: '13px', color: '#999' }}>
                          {dayjs(item.created_at).fromNow()}
                        </span>

                        {/* 状态标签 */}
                        {item.status === 'completed' && (
                          <Tag color="success" icon={<CheckCircleOutlined />}>
                            已完成
                          </Tag>
                        )}

                        {/* 完成信息 */}
                        {item.completed_at && item.completed_by_username && (
                          <span style={{ fontSize: '13px', color: '#52c41a' }}>
                            由 {item.completed_by_username} 于 {dayjs(item.completed_at).fromNow()} 完成
                          </span>
                        )}
                      </Space>
                    </div>

                    {/* 删除按钮 */}
                    {(user?.role === 'admin' || item.user_id === user?.id) && (
                      <div>
                        <Popconfirm
                          title="确认删除"
                          description="确定要删除这条建议吗？"
                          onConfirm={() => handleDelete(item.id)}
                          okText="确定"
                          cancelText="取消"
                        >
                          <Button
                            type="text"
                            danger
                            size="small"
                            icon={<DeleteOutlined />}
                          />
                        </Popconfirm>
                      </div>
                    )}
                  </div>
                </List.Item>
              )}
            />
          )}
        </Spin>
      </Card>
    </div>
  )
}

export default Suggestions
