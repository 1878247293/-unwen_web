import { useState, useEffect } from 'react'
import {
  Card,
  Button,
  Input,
  Table,
  Modal,
  Form,
  message,
  Space,
  Select,
  Tag,
  Popconfirm,
  Typography,
  Tooltip,
  Badge,
  Checkbox
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  LinkOutlined,
  SearchOutlined,
  StarOutlined,
  StarFilled,
  GlobalOutlined
} from '@ant-design/icons'
import websitesService from '../services/websitesService'

const { TextArea } = Input
const { Title, Text, Paragraph } = Typography
const { Option } = Select

const Websites = () => {
  const [websites, setWebsites] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [searchKeyword, setSearchKeyword] = useState('')
  const [categoryFilter, setCategoryFilter] = useState(undefined)
  const [favoriteFilter, setFavoriteFilter] = useState(undefined)

  // Modal状态
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [modalMode, setModalMode] = useState('create') // 'create' or 'edit'
  const [currentWebsite, setCurrentWebsite] = useState(null)
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)

  // 加载网站列表
  const loadWebsites = async () => {
    setLoading(true)
    try {
      const response = await websitesService.getWebsites({
        page,
        page_size: pageSize,
        keyword: keyword || undefined,
        category: categoryFilter,
        is_favorite: favoriteFilter
      })

      if (response.code === 200) {
        setWebsites(response.data.websites || [])
        setTotal(response.data.total || 0)
      }
    } catch (error) {
      message.error('加载网站列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 加载分类列表
  const loadCategories = async () => {
    try {
      const response = await websitesService.getCategories()
      if (response.code === 200) {
        setCategories(response.data.categories || [])
      }
    } catch (error) {
      console.error('加载分类列表失败', error)
    }
  }

  useEffect(() => {
    loadWebsites()
  }, [page, pageSize, keyword, categoryFilter, favoriteFilter])

  useEffect(() => {
    loadCategories()
  }, [])

  // 搜索
  const handleSearch = () => {
    setKeyword(searchKeyword)
    setPage(1)
  }

  // 打开创建Modal
  const handleCreate = () => {
    setModalMode('create')
    setCurrentWebsite(null)
    form.resetFields()
    form.setFieldsValue({ is_favorite: false }) // 确保收藏默认为false
    setIsModalVisible(true)
  }

  // 打开编辑Modal
  const handleEdit = (website) => {
    setModalMode('edit')
    setCurrentWebsite(website)
    form.setFieldsValue({
      name: website.name,
      url: website.url,
      category: website.category,
      description: website.description,
      is_favorite: website.is_favorite
    })
    setIsModalVisible(true)
  }

  // 提交表单（优化版）
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      setSubmitting(true)

      if (modalMode === 'create') {
        // 创建模式
        const response = await websitesService.createWebsite(values)
        if (response.code === 200) {
          message.success('网站添加成功', 1.5)
          setIsModalVisible(false)

          // 乐观更新：立即添加到列表顶部
          const newWebsite = response.data
          setWebsites(prev => [newWebsite, ...prev])
          setTotal(prev => prev + 1)

          // 重新加载分类（可能有新分类）
          loadCategories()
        }
      } else {
        // 编辑模式
        const response = await websitesService.updateWebsite(currentWebsite.id, values)
        if (response.code === 200) {
          message.success('网站更新成功', 1.5)
          setIsModalVisible(false)

          // 乐观更新：立即更新列表中的项
          const updatedWebsite = response.data
          setWebsites(prev =>
            prev.map(w => w.id === currentWebsite.id ? updatedWebsite : w)
          )

          // 重新加载分类
          loadCategories()
        }
      }
    } catch (error) {
      console.error('提交失败', error)
    } finally {
      setSubmitting(false)
    }
  }

  // 删除网站（乐观更新）
  const handleDelete = async (id) => {
    // 1. 立即从UI中移除（乐观更新）
    const deletedWebsite = websites.find(w => w.id === id)
    setWebsites(prevWebsites => prevWebsites.filter(w => w.id !== id))
    setTotal(prev => prev - 1)

    // 2. 显示即时反馈
    message.success('网站删除成功', 1)

    // 3. 后台调用API
    try {
      const response = await websitesService.deleteWebsite(id)

      // 如果API失败，恢复数据
      if (response.code !== 200) {
        setWebsites(prevWebsites => [...prevWebsites, deletedWebsite].sort((a, b) => b.id - a.id))
        setTotal(prev => prev + 1)
        message.error('删除网站失败，请重试')
      }
    } catch (error) {
      // API调用失败，恢复数据
      setWebsites(prevWebsites => [...prevWebsites, deletedWebsite].sort((a, b) => b.id - a.id))
      setTotal(prev => prev + 1)
      message.error('删除网站失败，请重试')
    }
  }

  // 切换收藏状态（乐观更新）
  const toggleFavorite = async (website) => {
    const newFavoriteStatus = !website.is_favorite

    // 1. 立即更新UI（乐观更新）
    setWebsites(prevWebsites =>
      prevWebsites.map(w =>
        w.id === website.id ? { ...w, is_favorite: newFavoriteStatus } : w
      )
    )

    // 2. 显示即时反馈
    message.success(newFavoriteStatus ? '已收藏' : '已取消收藏', 1)

    // 3. 后台调用API
    try {
      const response = await websitesService.updateWebsite(website.id, {
        is_favorite: newFavoriteStatus
      })

      // 如果API失败，回滚UI状态
      if (response.code !== 200) {
        setWebsites(prevWebsites =>
          prevWebsites.map(w =>
            w.id === website.id ? { ...w, is_favorite: !newFavoriteStatus } : w
          )
        )
        message.error('操作失败，请重试')
      }
    } catch (error) {
      // API调用失败，回滚UI状态
      setWebsites(prevWebsites =>
        prevWebsites.map(w =>
          w.id === website.id ? { ...w, is_favorite: !newFavoriteStatus } : w
        )
      )
      message.error('操作失败，请重试')
    }
  }

  // 打开链接
  const openLink = (url) => {
    window.open(url, '_blank')
  }

  // 分类颜色映射
  const categoryColors = {
    '学术搜索': 'blue',
    '论文数据库': 'green',
    '文献管理': 'purple',
    '引文分析': 'orange',
    '期刊资源': 'red',
    '学术工具': 'cyan',
    '数据集': 'magenta',
    '其他': 'default'
  }

  // 表格列定义
  const columns = [
    {
      title: '网站名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (text, record) => (
        <Space>
          <Button
            type="link"
            icon={<StarFilled style={{ color: record.is_favorite ? '#fadb14' : '#d9d9d9' }} />}
            onClick={() => toggleFavorite(record)}
            size="small"
          />
          <Text strong>{text}</Text>
        </Space>
      )
    },
    {
      title: '链接',
      dataIndex: 'url',
      key: 'url',
      ellipsis: true,
      render: (url) => (
        <Tooltip title={url}>
          <Button
            type="link"
            icon={<LinkOutlined />}
            onClick={() => openLink(url)}
            size="small"
          >
            访问
          </Button>
        </Tooltip>
      )
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category) => (
        category ? (
          <Tag color={categoryColors[category] || 'default'}>
            {category}
          </Tag>
        ) : (
          <Text type="secondary">未分类</Text>
        )
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (description) => (
        description ? (
          <Tooltip title={description}>
            <Paragraph ellipsis={{ rows: 1 }} style={{ margin: 0 }}>
              {description}
            </Paragraph>
          </Tooltip>
        ) : (
          <Text type="secondary">暂无描述</Text>
        )
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个网站吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />} size="small">
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* 标题 */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <GlobalOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              <Title level={3} style={{ margin: 0 }}>科研网站收藏</Title>
              <Badge count={total} style={{ backgroundColor: '#52c41a' }} />
            </Space>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              添加网站
            </Button>
          </div>

          {/* 搜索和筛选 */}
          <Space wrap>
            <Input
              placeholder="搜索网站名称、描述或链接"
              prefix={<SearchOutlined />}
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 300 }}
              allowClear
            />
            <Button type="primary" onClick={handleSearch}>
              搜索
            </Button>
            <Select
              placeholder="筛选分类"
              style={{ width: 150 }}
              value={categoryFilter}
              onChange={setCategoryFilter}
              allowClear
            >
              {categories.map(cat => (
                <Option key={cat} value={cat}>{cat}</Option>
              ))}
            </Select>
            <Select
              placeholder="筛选收藏"
              style={{ width: 120 }}
              value={favoriteFilter}
              onChange={setFavoriteFilter}
              allowClear
            >
              <Option value={true}>仅收藏</Option>
              <Option value={false}>未收藏</Option>
            </Select>
            {(keyword || categoryFilter !== undefined || favoriteFilter !== undefined) && (
              <Button
                onClick={() => {
                  setSearchKeyword('')
                  setKeyword('')
                  setCategoryFilter(undefined)
                  setFavoriteFilter(undefined)
                  setPage(1)
                }}
              >
                清除筛选
              </Button>
            )}
          </Space>

          {/* 表格 */}
          <Table
            dataSource={websites}
            columns={columns}
            rowKey="id"
            loading={loading}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              onChange: (p, ps) => {
                setPage(p)
                setPageSize(ps)
              },
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个网站`
            }}
          />
        </Space>
      </Card>

      {/* 创建/编辑Modal */}
      <Modal
        title={modalMode === 'create' ? '添加网站' : '编辑网站'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => setIsModalVisible(false)}
        confirmLoading={submitting}
        width={600}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="网站名称"
            rules={[{ required: true, message: '请输入网站名称' }]}
          >
            <Input placeholder="例如：Google Scholar" />
          </Form.Item>

          <Form.Item
            name="url"
            label="网站链接"
            rules={[
              { required: true, message: '请输入网站链接' },
              { type: 'url', message: '请输入有效的URL' }
            ]}
          >
            <Input placeholder="https://..." prefix={<LinkOutlined />} />
          </Form.Item>

          <Form.Item name="category" label="分类">
            <Select
              placeholder="选择或输入新分类"
              allowClear
              showSearch
              mode="tags"
              maxCount={1}
            >
              {categories.map(cat => (
                <Option key={cat} value={cat}>{cat}</Option>
              ))}
              <Option value="学术搜索">学术搜索</Option>
              <Option value="论文数据库">论文数据库</Option>
              <Option value="文献管理">文献管理</Option>
              <Option value="引文分析">引文分析</Option>
              <Option value="期刊资源">期刊资源</Option>
              <Option value="学术工具">学术工具</Option>
              <Option value="数据集">数据集</Option>
            </Select>
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea
              rows={3}
              placeholder="简要描述这个网站的用途和特点"
              maxLength={500}
              showCount
            />
          </Form.Item>

          <Form.Item name="is_favorite" valuePropName="checked" initialValue={false}>
            <Checkbox>
              <Space>
                <StarOutlined style={{ color: '#fadb14' }} />
                <span>标记为常用网站</span>
              </Space>
            </Checkbox>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Websites
