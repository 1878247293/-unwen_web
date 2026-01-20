import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Table,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Modal,
  message,
  Card,
  Row,
  Col,
  Pagination,
  Upload,
  Tabs
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  FileTextOutlined,
  ExportOutlined,
  ImportOutlined,
  DownloadOutlined
} from '@ant-design/icons'
import paperService from '../services/paperService'
import tagService from '../services/tagService'
import { useAuthStore } from '../store/authStore'
import useDebounce from '../hooks/useDebounce'

const { Search } = Input
const { Option } = Select

const Papers = () => {
  const navigate = useNavigate()
  const [urlSearchParams] = useSearchParams()
  const { user } = useAuthStore()

  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [tags, setTags] = useState([])
  const [selectedRowKeys, setSelectedRowKeys] = useState([])
  const [importModalVisible, setImportModalVisible] = useState(false)
  const [importing, setImporting] = useState(false)
  const [activeTab, setActiveTab] = useState('my') // 'my' 或 'shared'

  // 搜索关键词（实时更新）
  const [searchKeyword, setSearchKeyword] = useState('')
  // 防抖后的搜索关键词（延迟500ms更新）
  const debouncedKeyword = useDebounce(searchKeyword, 500)

  // 搜索和筛选参数
  const [searchParams, setSearchParams] = useState({
    keyword: '',
    year: null,
    reading_status: null,
    tag_id: urlSearchParams.get('tag') || null,
    only_my_papers: true, // 默认显示我的论文
    is_shared: null,
    page: 1,
    page_size: 20,
    sort_by: 'created_at',
    sort_order: 'desc'
  })

  // 当防抖后的关键词变化时，更新搜索参数
  useEffect(() => {
    setSearchParams(prev => ({
      ...prev,
      keyword: debouncedKeyword,
      page: 1
    }))
  }, [debouncedKeyword])

  // 加载论文列表
  const loadPapers = async () => {
    setLoading(true)
    try {
      // 过滤掉空值参数
      const params = Object.fromEntries(
        Object.entries(searchParams).filter(([_, v]) => v != null && v !== '')
      )

      const response = await paperService.getPapers(params)

      if (response.code === 200) {
        setPapers(response.data.papers)
        setTotal(response.data.total)
      } else {
        message.error(response.message || '加载论文列表失败')
      }
    } catch (error) {
      message.error('加载论文列表失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 加载标签列表
  const loadTags = async () => {
    try {
      const response = await tagService.getTags()
      if (response.code === 200) {
        setTags(response.data.tags)
      }
    } catch (error) {
      console.error('加载标签失败:', error)
    }
  }

  // Tab切换处理
  const handleTabChange = (key) => {
    setActiveTab(key)
    if (key === 'my') {
      // "我的论文"：只显示我创建的论文（不管是否共享）
      setSearchParams({
        ...searchParams,
        only_my_papers: true,
        is_shared: null,
        page: 1
      })
    } else if (key === 'shared') {
      // "共享论文库"：显示所有共享的论文（包括我的和别人的）
      setSearchParams({
        ...searchParams,
        only_my_papers: null,
        is_shared: true,
        page: 1
      })
    }
    setSelectedRowKeys([]) // 清空选中项
  }

  // 初始加载
  useEffect(() => {
    loadTags()
  }, [])

  useEffect(() => {
    loadPapers()
  }, [searchParams])

  // 搜索 - 直接更新searchKeyword，防抖hook会自动处理
  const handleSearch = (value) => {
    setSearchKeyword(value)
  }

  // 搜索框内容变化 - 实时更新状态
  const handleSearchChange = (e) => {
    setSearchKeyword(e.target.value)
  }

  // 筛选改变
  const handleFilterChange = (key, value) => {
    setSearchParams({
      ...searchParams,
      [key]: value,
      page: 1
    })
  }

  // 分页改变
  const handlePageChange = (page, pageSize) => {
    setSearchParams({
      ...searchParams,
      page,
      page_size: pageSize
    })
  }

  // 删除论文（优化：乐观更新）
  const handleDelete = useCallback((record) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除论文《${record.title}》吗？此操作不可恢复。`,
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        // 乐观更新：先从列表中移除
        setPapers(prev => prev.filter(p => p.id !== record.id))
        setTotal(prev => prev - 1)

        try {
          const response = await paperService.deletePaper(record.id)

          if (response.code === 200) {
            message.success('论文删除成功')
          } else {
            message.error(response.message || '论文删除失败')
            // 失败时重新加载
            loadPapers()
          }
        } catch (error) {
          message.error('论文删除失败: ' + (error.response?.data?.detail || error.message))
          // 失败时重新加载
          loadPapers()
        }
      }
    })
  }, [])

  // 下载论文PDF
  const handleDownload = useCallback(async (record) => {
    if (!record.pdf_path) {
      message.warning('该论文没有PDF文件')
      return
    }

    try {
      // 生成文件名
      const filename = `${record.title}.pdf`
      await paperService.downloadPdf(record.id, filename)
      message.success('PDF下载成功')
    } catch (error) {
      message.error('PDF下载失败: ' + (error.message || '未知错误'))
    }
  }, [])

  // 阅读状态标签颜色
  const getStatusColor = (status) => {
    const colorMap = {
      'unread': 'default',
      'reading': 'processing',
      'read': 'success'
    }
    return colorMap[status] || 'default'
  }

  const getStatusText = (status) => {
    const textMap = {
      'unread': '未读',
      'reading': '在读',
      'read': '已读'
    }
    return textMap[status] || status
  }

  // 批量导出BibTeX
  const handleBatchExport = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要导出的论文')
      return
    }

    const token = localStorage.getItem('auth-storage')
    let authToken = ''

    if (token) {
      try {
        const parsed = JSON.parse(token)
        authToken = parsed.state?.token || ''
      } catch (e) {
        console.error('Failed to parse token', e)
      }
    }

    // 批量导出
    const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/papers/export/bibtex/batch`

    fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(selectedRowKeys)
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('导出失败')
        }
        return response.blob()
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `papers_export.bib`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        message.success(`成功导出${selectedRowKeys.length}篇论文`)
        setSelectedRowKeys([])
      })
      .catch(error => {
        message.error('导出失败: ' + error.message)
      })
  }

  // 导出所有论文
  const handleExportAll = () => {
    const token = localStorage.getItem('auth-storage')
    let authToken = ''

    if (token) {
      try {
        const parsed = JSON.parse(token)
        authToken = parsed.state?.token || ''
      } catch (e) {
        console.error('Failed to parse token', e)
      }
    }

    const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/papers/export/bibtex/all`

    fetch(url, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('导出失败')
        }
        return response.blob()
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `my_papers.bib`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        message.success('导出成功')
      })
      .catch(error => {
        message.error('导出失败: ' + error.message)
      })
  }

  // 导入BibTeX
  const handleImportBibtex = (file) => {
    const token = localStorage.getItem('auth-storage')
    let authToken = ''

    if (token) {
      try {
        const parsed = JSON.parse(token)
        authToken = parsed.state?.token || ''
      } catch (e) {
        console.error('Failed to parse token', e)
        return false
      }
    }

    setImporting(true)

    const formData = new FormData()
    formData.append('file', file)

    fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/papers/import/bibtex`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        setImporting(false)
        setImportModalVisible(false)

        if (data.code === 200) {
          message.success(data.message || '导入成功')
          loadPapers()
        } else {
          message.error(data.message || '导入失败')
        }
      })
      .catch(error => {
        setImporting(false)
        message.error('导入失败: ' + error.message)
      })

    return false // 阻止自动上传
  }

  // 表格列定义（使用useMemo缓存，避免每次渲染都重新创建）
  const columns = useMemo(() => [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: '30%',
      render: (text, record) => (
        <a onClick={() => navigate(`/papers/${record.id}`)}>
          {text}
        </a>
      ),
    },
    {
      title: '作者',
      dataIndex: 'authors',
      key: 'authors',
      width: '20%',
      ellipsis: true,
    },
    {
      title: '期刊/会议',
      dataIndex: 'journal',
      key: 'journal',
      width: '15%',
      ellipsis: true,
    },
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      width: '80px',
    },
    {
      title: '状态',
      dataIndex: 'reading_status',
      key: 'reading_status',
      width: '80px',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: '150px',
      render: (tags) => (
        <>
          {tags && tags.length > 0 ? (
            tags.slice(0, 2).map((tag) => (
              <Tag key={tag.id} color={tag.color} style={{ marginBottom: '4px' }}>
                {tag.name}
              </Tag>
            ))
          ) : (
            '-'
          )}
          {tags && tags.length > 2 && (
            <Tag style={{ marginBottom: '4px' }}>+{tags.length - 2}</Tag>
          )}
        </>
      ),
    },
    {
      title: 'PDF',
      dataIndex: 'pdf_path',
      key: 'pdf_path',
      width: '60px',
      render: (path) => path ? <FileTextOutlined style={{ color: '#1890ff' }} /> : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: '200px',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/papers/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record)}
            disabled={!record.pdf_path}
          >
            下载
          </Button>
          {(user?.role === 'admin' || record.created_by === user?.id) && (
            <>
              <Button
                type="link"
                size="small"
                icon={<EditOutlined />}
                onClick={() => navigate(`/papers/${record.id}/edit`)}
              >
                编辑
              </Button>
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
                onClick={() => handleDelete(record)}
              >
                删除
              </Button>
            </>
          )}
        </Space>
      ),
    },
  ], [user, navigate, handleDelete, handleDownload])

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        {/* Tab切换 */}
        <Tabs
          activeKey={activeTab}
          onChange={handleTabChange}
          style={{ marginBottom: 16 }}
          items={[
            {
              key: 'my',
              label: '我的论文',
              children: null
            },
            {
              key: 'shared',
              label: '共享论文库',
              children: null
            }
          ]}
        />

        {/* 搜索和筛选栏 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="搜索标题、作者、关键词"
              allowClear
              value={searchKeyword}
              onChange={handleSearchChange}
              enterButton={<SearchOutlined />}
              onSearch={handleSearch}
            />
          </Col>
          <Col xs={12} sm={6} md={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="标签筛选"
              allowClear
              value={searchParams.tag_id}
              onChange={(value) => handleFilterChange('tag_id', value)}
            >
              {tags.map((tag) => (
                <Option key={tag.id} value={tag.id}>
                  <Tag color={tag.color} style={{ marginRight: 4 }}>
                    {tag.name}
                  </Tag>
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={12} sm={6} md={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="阅读状态"
              allowClear
              onChange={(value) => handleFilterChange('reading_status', value)}
            >
              <Option value="unread">未读</Option>
              <Option value="reading">在读</Option>
              <Option value="read">已读</Option>
            </Select>
          </Col>
          <Col xs={12} sm={6} md={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="排序方式"
              defaultValue="created_at"
              onChange={(value) => handleFilterChange('sort_by', value)}
            >
              <Option value="created_at">创建时间</Option>
              <Option value="updated_at">更新时间</Option>
              <Option value="title">标题</Option>
              <Option value="year">年份</Option>
            </Select>
          </Col>
          <Col xs={24} sm={24} md={12} style={{ textAlign: 'right' }}>
            <Space>
              <Button
                icon={<ImportOutlined />}
                onClick={() => setImportModalVisible(true)}
              >
                导入BibTeX
              </Button>
              <Button
                icon={<ExportOutlined />}
                onClick={handleBatchExport}
                disabled={selectedRowKeys.length === 0}
              >
                批量导出 ({selectedRowKeys.length})
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={handleExportAll}
              >
                导出全部
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/papers/add')}
              >
                添加论文
              </Button>
            </Space>
          </Col>
        </Row>

        {/* 论文列表表格 */}
        <Table
          columns={columns}
          dataSource={papers}
          rowKey="id"
          loading={loading}
          pagination={false}
          scroll={{ x: 1000 }}
          rowSelection={{
            selectedRowKeys,
            onChange: (selectedKeys) => setSelectedRowKeys(selectedKeys),
          }}
        />

        {/* 分页 */}
        <div style={{ marginTop: 16, textAlign: 'right' }}>
          <Pagination
            current={searchParams.page}
            pageSize={searchParams.page_size}
            total={total}
            showSizeChanger
            showQuickJumper
            showTotal={(total) => `共 ${total} 篇论文`}
            onChange={handlePageChange}
            pageSizeOptions={['10', '20', '50', '100']}
          />
        </div>
      </Card>

      {/* 导入BibTeX Modal */}
      <Modal
        title="导入BibTeX文件"
        open={importModalVisible}
        onCancel={() => setImportModalVisible(false)}
        footer={null}
      >
        <Upload.Dragger
          accept=".bib,.bibtex"
          beforeUpload={handleImportBibtex}
          showUploadList={false}
        >
          <p className="ant-upload-drag-icon">
            <ImportOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽BibTeX文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持.bib和.bibtex格式文件，会自动解析并批量导入论文信息
          </p>
        </Upload.Dragger>
        {importing && (
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            导入中，请稍候...
          </div>
        )}
      </Modal>
    </div>
  )
}

export default Papers
