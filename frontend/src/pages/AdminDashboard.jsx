/**
 * 管理员Dashboard页面
 */
import { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Tag,
  Spin,
  message
} from 'antd'
import {
  UserOutlined,
  FileTextOutlined,
  TagsOutlined,
  EditOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import adminService from '../services/adminService'

function AdminDashboard() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setLoading(true)
    try {
      const response = await adminService.getOverview()
      if (response.code === 200) {
        setStats(response.data)
      } else {
        message.error(response.message || '加载统计数据失败')
      }
    } catch (error) {
      message.error('加载统计数据失败: ' + (error.message || error))
    } finally {
      setLoading(false)
    }
  }

  if (loading || !stats) {
    return (
      <div style={{ padding: '100px 0', textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    )
  }

  const { user_stats, user_role_stats, paper_stats, total_notes, total_tags, recent_activity } = stats

  return (
    <div style={{ padding: '24px' }}>
      <h2 style={{ marginBottom: '24px' }}>管理员控制台</h2>

      {/* 核心统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总用户数"
              value={user_stats.total}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>
              管理员: {user_role_stats.admin} / 普通用户: {user_role_stats.user}
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总论文数"
              value={paper_stats.total}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>
              已读: {paper_stats.read} / 在读: {paper_stats.reading}
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总笔记数"
              value={total_notes}
              prefix={<EditOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总标签数"
              value={total_tags}
              prefix={<TagsOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 用户状态和阅读状态 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col xs={24} md={12}>
          <Card title="用户状态分布">
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>激活用户</span>
                <span><Tag color="success">{user_stats.active}</Tag></span>
              </div>
              <Progress
                percent={(user_stats.active / user_stats.total * 100).toFixed(1)}
                strokeColor="#52c41a"
                showInfo={false}
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>待审核用户</span>
                <span><Tag color="warning">{user_stats.pending}</Tag></span>
              </div>
              <Progress
                percent={(user_stats.pending / user_stats.total * 100).toFixed(1)}
                strokeColor="#faad14"
                showInfo={false}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>禁用用户</span>
                <span><Tag color="default">{user_stats.disabled}</Tag></span>
              </div>
              <Progress
                percent={(user_stats.disabled / user_stats.total * 100).toFixed(1)}
                strokeColor="#d9d9d9"
                showInfo={false}
              />
            </div>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="论文阅读状态">
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>未读</span>
                <span><Tag color="default">{paper_stats.unread}</Tag></span>
              </div>
              <Progress
                percent={(paper_stats.unread / paper_stats.total * 100).toFixed(1)}
                strokeColor="#d9d9d9"
                showInfo={false}
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>在读</span>
                <span><Tag color="processing">{paper_stats.reading}</Tag></span>
              </div>
              <Progress
                percent={(paper_stats.reading / paper_stats.total * 100).toFixed(1)}
                strokeColor="#1890ff"
                showInfo={false}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>已读</span>
                <span><Tag color="success">{paper_stats.read}</Tag></span>
              </div>
              <Progress
                percent={(paper_stats.read / paper_stats.total * 100).toFixed(1)}
                strokeColor="#52c41a"
                showInfo={false}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* 最近活动 */}
      <Row gutter={16}>
        <Col xs={24}>
          <Card title="最近7天活动">
            <Row gutter={16}>
              <Col xs={24} sm={8}>
                <Card>
                  <Statistic
                    title="新增用户"
                    value={recent_activity.new_users_7d}
                    prefix={<TeamOutlined />}
                    suffix="人"
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card>
                  <Statistic
                    title="新增论文"
                    value={recent_activity.new_papers_7d}
                    prefix={<FileTextOutlined />}
                    suffix="篇"
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card>
                  <Statistic
                    title="新增笔记"
                    value={recent_activity.new_notes_7d}
                    prefix={<EditOutlined />}
                    suffix="条"
                  />
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default AdminDashboard
