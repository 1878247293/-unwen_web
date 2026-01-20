import { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Progress,
  Statistic,
  Typography,
  Space,
  Spin,
  Alert,
  Switch,
  message,
  Divider,
  Tag
} from 'antd'
import {
  DashboardOutlined,
  DatabaseOutlined,
  CloudServerOutlined,
  TeamOutlined,
  FileTextOutlined,
  CommentOutlined,
  BulbOutlined,
  GlobalOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined
} from '@ant-design/icons'
import systemService from '../services/systemService'
import dayjs from 'dayjs'

const { Title, Text, Paragraph } = Typography

const SystemMonitor = () => {
  const [loading, setLoading] = useState(true)
  const [resources, setResources] = useState(null)
  const [statistics, setStatistics] = useState(null)
  const [storage, setStorage] = useState(null)
  const [health, setHealth] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(null)

  // 加载所有数据
  const loadAllData = async () => {
    try {
      setLoading(true)
      const [resourcesRes, statisticsRes, storageRes, healthRes] = await Promise.all([
        systemService.getResources(),
        systemService.getStatistics(),
        systemService.getStorage(),
        systemService.getHealth()
      ])

      if (resourcesRes.code === 200) {
        setResources(resourcesRes.data)
      }
      if (statisticsRes.code === 200) {
        setStatistics(statisticsRes.data)
      }
      if (storageRes.code === 200) {
        setStorage(storageRes.data)
      }
      if (healthRes.code === 200) {
        setHealth(healthRes.data)
      }

      setLastUpdate(new Date())
    } catch (error) {
      message.error('加载监控数据失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 初始加载
  useEffect(() => {
    loadAllData()
  }, [])

  // 自动刷新
  useEffect(() => {
    let interval
    if (autoRefresh) {
      interval = setInterval(() => {
        loadAllData()
      }, 30000) // 每30秒刷新一次
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh])

  // 获取进度条颜色
  const getProgressColor = (percent) => {
    if (percent >= 90) return '#ff4d4f'
    if (percent >= 80) return '#faad14'
    return '#52c41a'
  }

  // 获取健康状态标签
  const getHealthTag = () => {
    if (!health) return null

    const statusConfig = {
      healthy: { color: 'success', icon: <CheckCircleOutlined />, text: '健康' },
      warning: { color: 'warning', icon: <WarningOutlined />, text: '警告' },
      critical: { color: 'error', icon: <CloseCircleOutlined />, text: '严重' }
    }

    const config = statusConfig[health.overall] || statusConfig.healthy

    return (
      <Tag icon={config.icon} color={config.color} style={{ fontSize: '14px' }}>
        {config.text}
      </Tag>
    )
  }

  if (loading && !resources) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" tip="加载监控数据..." />
      </div>
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ marginBottom: '8px' }}>
            <DashboardOutlined /> 资源监控
          </Title>
          <Space>
            {getHealthTag()}
            {lastUpdate && (
              <Text type="secondary">
                最后更新：{dayjs(lastUpdate).format('HH:mm:ss')}
              </Text>
            )}
          </Space>
        </div>
        <Space>
          <Space>
            <Text>自动刷新</Text>
            <Switch checked={autoRefresh} onChange={setAutoRefresh} />
          </Space>
          <Card
            size="small"
            hoverable
            onClick={loadAllData}
            style={{ cursor: 'pointer' }}
          >
            <Space>
              <ReloadOutlined spin={loading} />
              刷新
            </Space>
          </Card>
        </Space>
      </div>

      {/* 健康状态警告 */}
      {health && health.issues && health.issues.length > 0 && (
        <Alert
          message="系统警告"
          description={
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              {health.issues.map((issue, index) => (
                <li key={index}>{issue}</li>
              ))}
            </ul>
          }
          type={health.overall === 'critical' ? 'error' : 'warning'}
          showIcon
          style={{ marginBottom: '24px' }}
        />
      )}

      {/* 系统资源 */}
      {resources && (
        <>
          <Title level={4}>
            <CloudServerOutlined /> 系统资源
          </Title>
          <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
            <Col xs={24} sm={12} lg={8}>
              <Card>
                <Statistic
                  title="CPU 使用率"
                  value={resources.cpu.percent}
                  suffix="%"
                  valueStyle={{ color: getProgressColor(resources.cpu.percent) }}
                />
                <Progress
                  percent={resources.cpu.percent}
                  strokeColor={getProgressColor(resources.cpu.percent)}
                  status="active"
                />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {resources.cpu.count} 核心
                </Text>
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Card>
                <Statistic
                  title="内存使用"
                  value={resources.memory.percent}
                  suffix="%"
                  valueStyle={{ color: getProgressColor(resources.memory.percent) }}
                />
                <Progress
                  percent={resources.memory.percent}
                  strokeColor={getProgressColor(resources.memory.percent)}
                  status="active"
                />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {resources.memory.used_gb} GB / {resources.memory.total_gb} GB
                </Text>
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Card>
                <Statistic
                  title="磁盘使用"
                  value={resources.disk.percent}
                  suffix="%"
                  valueStyle={{ color: getProgressColor(resources.disk.percent) }}
                />
                <Progress
                  percent={resources.disk.percent}
                  strokeColor={getProgressColor(resources.disk.percent)}
                  status="active"
                />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {resources.disk.used_gb} GB / {resources.disk.total_gb} GB
                </Text>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* 数据库统计 */}
      {statistics && (
        <>
          <Title level={4}>
            <DatabaseOutlined /> 数据库统计
          </Title>
          <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
            <Col xs={12} sm={8} lg={6}>
              <Card>
                <Statistic
                  title="用户总数"
                  value={statistics.users.total}
                  prefix={<TeamOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  活跃: {statistics.users.active} | 待审: {statistics.users.pending}
                </Text>
              </Card>
            </Col>
            <Col xs={12} sm={8} lg={6}>
              <Card>
                <Statistic
                  title="论文总数"
                  value={statistics.papers.total}
                  prefix={<FileTextOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={8} lg={6}>
              <Card>
                <Statistic
                  title="讨论总数"
                  value={statistics.discussions.total}
                  prefix={<CommentOutlined />}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={8} lg={6}>
              <Card>
                <Statistic
                  title="评论总数"
                  value={statistics.comments.total}
                  prefix={<CommentOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={8} lg={6}>
              <Card>
                <Statistic
                  title="想法总数"
                  value={statistics.ideas.total}
                  prefix={<BulbOutlined />}
                  valueStyle={{ color: '#eb2f96' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={8} lg={6}>
              <Card>
                <Statistic
                  title="网站收藏"
                  value={statistics.websites.total}
                  prefix={<GlobalOutlined />}
                  valueStyle={{ color: '#13c2c2' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={8} lg={6}>
              <Card>
                <Statistic
                  title="笔记总数"
                  value={statistics.notes.total}
                  valueStyle={{ color: '#2f54eb' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={8} lg={6}>
              <Card>
                <Statistic
                  title="标签总数"
                  value={statistics.tags.total}
                  valueStyle={{ color: '#fa8c16' }}
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* 存储使用情况 */}
      {storage && (
        <>
          <Title level={4}>
            <DatabaseOutlined /> 存储使用情况
          </Title>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="论文文件"
                  value={storage.uploads.papers.size_formatted}
                  valueStyle={{ fontSize: '20px' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="PDF 文件"
                  value={storage.uploads.pdfs.size_formatted}
                  valueStyle={{ fontSize: '20px' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="头像文件"
                  value={storage.uploads.avatars.size_formatted}
                  valueStyle={{ fontSize: '20px' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="数据库"
                  value={storage.database.size_formatted}
                  valueStyle={{ fontSize: '20px' }}
                />
              </Card>
            </Col>
            <Col xs={24}>
              <Card>
                <Statistic
                  title="总存储占用"
                  value={storage.total.size_formatted}
                  valueStyle={{ fontSize: '24px', color: '#1890ff' }}
                />
              </Card>
            </Col>
          </Row>
        </>
      )}
    </div>
  )
}

export default SystemMonitor
