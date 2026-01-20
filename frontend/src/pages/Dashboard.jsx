import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  Row,
  Col,
  Statistic,
  List,
  Tag,
  Progress,
  Space,
  Spin,
  message,
  Empty
} from 'antd'
import {
  FileTextOutlined,
  BookOutlined,
  TagOutlined,
  ReadOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import statsService from '../services/statsService'

export default function Dashboard() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total_papers: 0,
    total_notes: 0,
    total_tags: 0,
    reading_stats: {
      unread: 0,
      reading: 0,
      read: 0
    },
    recent_papers: []
  })

  // 加载统计数据
  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setLoading(true)
    try {
      const response = await statsService.getDashboardStats()
      if (response.code === 200) {
        setStats(response.data)
      } else {
        message.error(response.message || '加载统计数据失败')
      }
    } catch (error) {
      message.error('加载统计数据失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 计算阅读进度百分比
  const getReadingPercentage = () => {
    const total = stats.reading_stats.unread + stats.reading_stats.reading + stats.reading_stats.read
    if (total === 0) return 0
    return Math.round((stats.reading_stats.read / total) * 100)
  }

  // 获取阅读状态标签
  const getStatusTag = (status) => {
    const statusMap = {
      'unread': { color: 'default', text: '未读' },
      'reading': { color: 'processing', text: '在读' },
      'read': { color: 'success', text: '已读' }
    }
    const config = statusMap[status] || { color: 'default', text: status }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  const readingPercentage = getReadingPercentage()

  return (
    <div>
      <h1>仪表盘</h1>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} sm={12} lg={8}>
          <Card hoverable onClick={() => navigate('/papers')}>
            <Statistic
              title="我的论文"
              value={stats.total_papers}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card hoverable>
            <Statistic
              title="我的笔记"
              value={stats.total_notes}
              prefix={<BookOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card hoverable>
            <Statistic
              title="我的标签"
              value={stats.total_tags}
              prefix={<TagOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 阅读进度可视化 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="阅读进度" bordered={false}>
            <div style={{ marginBottom: 24 }}>
              <Progress
                percent={readingPercentage}
                status="active"
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
              <p style={{ marginTop: 8, color: '#666' }}>
                已完成 {stats.reading_stats.read} / {stats.total_papers} 篇论文
              </p>
            </div>

            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="未读"
                  value={stats.reading_stats.unread}
                  valueStyle={{ color: '#999', fontSize: '20px' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="在读"
                  value={stats.reading_stats.reading}
                  valueStyle={{ color: '#1890ff', fontSize: '20px' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="已读"
                  value={stats.reading_stats.read}
                  valueStyle={{ color: '#52c41a', fontSize: '20px' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 阅读统计饼图数据 */}
        <Col xs={24} lg={12}>
          <Card title="阅读状态分布" bordered={false}>
            <div style={{ padding: '20px 0' }}>
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span>
                      <Tag color="default">未读</Tag>
                      {stats.reading_stats.unread} 篇
                    </span>
                    <span>{stats.total_papers > 0 ? Math.round((stats.reading_stats.unread / stats.total_papers) * 100) : 0}%</span>
                  </div>
                  <Progress
                    percent={stats.total_papers > 0 ? Math.round((stats.reading_stats.unread / stats.total_papers) * 100) : 0}
                    strokeColor="#999"
                    showInfo={false}
                  />
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span>
                      <Tag color="processing">在读</Tag>
                      {stats.reading_stats.reading} 篇
                    </span>
                    <span>{stats.total_papers > 0 ? Math.round((stats.reading_stats.reading / stats.total_papers) * 100) : 0}%</span>
                  </div>
                  <Progress
                    percent={stats.total_papers > 0 ? Math.round((stats.reading_stats.reading / stats.total_papers) * 100) : 0}
                    strokeColor="#1890ff"
                    showInfo={false}
                  />
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span>
                      <Tag color="success">已读</Tag>
                      {stats.reading_stats.read} 篇
                    </span>
                    <span>{stats.total_papers > 0 ? Math.round((stats.reading_stats.read / stats.total_papers) * 100) : 0}%</span>
                  </div>
                  <Progress
                    percent={stats.total_papers > 0 ? Math.round((stats.reading_stats.read / stats.total_papers) * 100) : 0}
                    strokeColor="#52c41a"
                    showInfo={false}
                  />
                </div>
              </Space>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 最近阅读记录 */}
      <Card
        title={
          <span>
            <ClockCircleOutlined style={{ marginRight: 8 }} />
            最近阅读
          </span>
        }
        extra={
          <a onClick={() => navigate('/papers')}>查看全部</a>
        }
        style={{ marginTop: 24 }}
      >
        {stats.recent_papers.length > 0 ? (
          <List
            dataSource={stats.recent_papers}
            renderItem={(paper) => (
              <List.Item
                key={paper.id}
                actions={[
                  getStatusTag(paper.reading_status),
                  <a onClick={() => navigate(`/papers/${paper.id}`)}>查看</a>
                ]}
                style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/papers/${paper.id}`)}
              >
                <List.Item.Meta
                  avatar={<ReadOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
                  title={paper.title}
                  description={
                    <Space split="|">
                      {paper.authors && <span>{paper.authors}</span>}
                      {paper.journal && <span>{paper.journal}</span>}
                      {paper.year && <span>{paper.year}</span>}
                      <span style={{ color: '#999' }}>
                        {new Date(paper.updated_at).toLocaleDateString('zh-CN')}
                      </span>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty
            description="暂无阅读记录"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Card>
    </div>
  )
}
