import { useState, useEffect } from 'react'
import {
  Card,
  Button,
  Input,
  List,
  Modal,
  message,
  Space,
  Pagination,
  Empty,
  Tag,
  Popconfirm,
  Typography
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  BulbOutlined,
  SearchOutlined
} from '@ant-design/icons'
import ideasService from '../services/ideasService'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import ReactMarkdown from 'react-markdown'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const { TextArea } = Input
const { Title, Paragraph } = Typography

const Ideas = () => {
  const [ideas, setIdeas] = useState([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [keyword, setKeyword] = useState('')
  const [searchKeyword, setSearchKeyword] = useState('')

  // Modal状态
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [modalMode, setModalMode] = useState('create') // 'create' or 'edit'
  const [currentIdea, setCurrentIdea] = useState(null)
  const [modalForm, setModalForm] = useState({ title: '', references: '', content: '' })
  const [submitting, setSubmitting] = useState(false)

  // 查看详情Modal
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedIdea, setSelectedIdea] = useState(null)

  // 加载想法列表
  const loadIdeas = async () => {
    setLoading(true)
    try {
      const response = await ideasService.getIdeas({
        page,
        page_size: pageSize,
        keyword: keyword || undefined
      })

      if (response.code === 200) {
        setIdeas(response.data.ideas || [])
        setTotal(response.data.total || 0)
      }
    } catch (error) {
      message.error('加载想法列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadIdeas()
  }, [page, pageSize, keyword])

  // 搜索
  const handleSearch = () => {
    setKeyword(searchKeyword)
    setPage(1)
  }

  // 打开创建Modal
  const handleCreate = () => {
    setModalMode('create')
    setCurrentIdea(null)
    setModalForm({ title: '', references: '', content: '' })
    setIsModalVisible(true)
  }

  // 打开编辑Modal
  const handleEdit = (idea) => {
    setModalMode('edit')
    setCurrentIdea(idea)
    setModalForm({
      title: idea.title || '',
      references: idea.references || '',
      content: idea.content || ''
    })
    setIsModalVisible(true)
  }

  // 提交创建/编辑
  const handleSubmit = async () => {
    if (!modalForm.content.trim()) {
      message.warning('请输入想法内容')
      return
    }

    setSubmitting(true)
    try {
      if (modalMode === 'create') {
        const response = await ideasService.createIdea(modalForm)
        if (response.code === 200) {
          message.success('想法创建成功')
          setIsModalVisible(false)
          loadIdeas()
        }
      } else {
        const response = await ideasService.updateIdea(currentIdea.id, modalForm)
        if (response.code === 200) {
          message.success('想法更新成功')
          setIsModalVisible(false)
          loadIdeas()
        }
      }
    } catch (error) {
      message.error(modalMode === 'create' ? '创建失败' : '更新失败')
    } finally {
      setSubmitting(false)
    }
  }

  // 删除想法
  const handleDelete = async (ideaId) => {
    try {
      const response = await ideasService.deleteIdea(ideaId)
      if (response.code === 200) {
        message.success('想法删除成功')
        loadIdeas()
      }
    } catch (error) {
      message.error('删除失败')
    }
  }

  // 查看详情
  const handleViewDetail = (idea) => {
    setSelectedIdea(idea)
    setDetailModalVisible(true)
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={2} style={{ margin: 0 }}>
            <BulbOutlined style={{ color: '#faad14', marginRight: '12px' }} />
            想法收集
          </Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            记录新想法
          </Button>
        </div>

        {/* 搜索栏 */}
        <div style={{ marginBottom: '16px' }}>
          <Space>
            <Input
              placeholder="搜索想法标题或内容"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: '300px' }}
              prefix={<SearchOutlined />}
            />
            <Button onClick={handleSearch}>搜索</Button>
            {keyword && (
              <Button
                onClick={() => {
                  setKeyword('')
                  setSearchKeyword('')
                  setPage(1)
                }}
              >
                清除搜索
              </Button>
            )}
          </Space>
        </div>

        {/* 统计信息 */}
        <div style={{ marginBottom: '16px', color: '#666' }}>
          共 {total} 条想法
        </div>

        {/* 想法列表 */}
        <List
          loading={loading}
          dataSource={ideas}
          locale={{
            emptyText: (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="还没有记录任何想法"
              >
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  记录第一个想法
                </Button>
              </Empty>
            )
          }}
          renderItem={(idea) => (
            <List.Item
              key={idea.id}
              actions={[
                <Button
                  type="link"
                  size="small"
                  onClick={() => handleViewDetail(idea)}
                >
                  查看详情
                </Button>,
                <Button
                  type="link"
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => handleEdit(idea)}
                >
                  编辑
                </Button>,
                <Popconfirm
                  title="确定删除这个想法吗？"
                  onConfirm={() => handleDelete(idea.id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                    删除
                  </Button>
                </Popconfirm>
              ]}
            >
              <List.Item.Meta
                title={
                  <div>
                    {idea.title ? (
                      <span style={{ fontSize: '16px', fontWeight: 'bold' }}>
                        {idea.title}
                      </span>
                    ) : (
                      <span style={{ fontSize: '16px', color: '#999', fontStyle: 'italic' }}>
                        （无标题）
                      </span>
                    )}
                    <span style={{ marginLeft: '12px', fontSize: '12px', color: '#999' }}>
                      {dayjs(idea.created_at).fromNow()}
                    </span>
                  </div>
                }
                description={
                  <div style={{ marginTop: '8px' }}>
                    <Paragraph
                      ellipsis={{ rows: 3 }}
                      style={{ margin: 0, color: '#666', whiteSpace: 'pre-wrap' }}
                    >
                      {idea.content_preview || idea.content}
                    </Paragraph>
                  </div>
                }
              />
            </List.Item>
          )}
        />

        {/* 分页 */}
        {total > 0 && (
          <div style={{ marginTop: '24px', textAlign: 'center' }}>
            <Pagination
              current={page}
              pageSize={pageSize}
              total={total}
              onChange={(newPage, newPageSize) => {
                setPage(newPage)
                if (newPageSize !== pageSize) {
                  setPageSize(newPageSize)
                  setPage(1)
                }
              }}
              showSizeChanger
              showTotal={(total) => `共 ${total} 条`}
            />
          </div>
        )}
      </Card>

      {/* 创建/编辑Modal */}
      <Modal
        title={modalMode === 'create' ? '记录新想法' : '编辑想法'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => setIsModalVisible(false)}
        okText={modalMode === 'create' ? '创建' : '保存'}
        cancelText="取消"
        confirmLoading={submitting}
        width={700}
      >
        <div>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              标题（可选）
            </label>
            <Input
              placeholder="给这个想法起个标题"
              value={modalForm.title}
              onChange={(e) => setModalForm({ ...modalForm, title: e.target.value })}
              maxLength={200}
              showCount
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              参考文献（可选）
            </label>
            <TextArea
              placeholder="记录相关的参考文献、论文出处等..."
              value={modalForm.references}
              onChange={(e) => setModalForm({ ...modalForm, references: e.target.value })}
              rows={4}
              maxLength={2000}
              showCount
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              内容 <span style={{ color: 'red' }}>*</span>
            </label>
            <TextArea
              placeholder="记录你的想法、灵感或思考...&#10;支持 Markdown 格式"
              value={modalForm.content}
              onChange={(e) => setModalForm({ ...modalForm, content: e.target.value })}
              rows={12}
              maxLength={10000}
              showCount
            />
          </div>
        </div>
      </Modal>

      {/* 详情Modal */}
      <Modal
        title={selectedIdea?.title || '（无标题）'}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="edit" type="primary" icon={<EditOutlined />} onClick={() => {
            setDetailModalVisible(false)
            handleEdit(selectedIdea)
          }}>
            编辑
          </Button>,
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {selectedIdea && (
          <div>
            <div style={{ marginBottom: '16px', color: '#999', fontSize: '12px' }}>
              创建时间：{dayjs(selectedIdea.created_at).format('YYYY-MM-DD HH:mm:ss')}
              {selectedIdea.updated_at && selectedIdea.updated_at !== selectedIdea.created_at && (
                <span style={{ marginLeft: '16px' }}>
                  更新时间：{dayjs(selectedIdea.updated_at).format('YYYY-MM-DD HH:mm:ss')}
                </span>
              )}
            </div>

            {selectedIdea.references && (
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#1890ff' }}>
                  参考文献
                </div>
                <div style={{
                  padding: '12px',
                  backgroundColor: '#f0f5ff',
                  borderRadius: '4px',
                  whiteSpace: 'pre-wrap',
                  color: '#666',
                  fontSize: '14px'
                }}>
                  {selectedIdea.references}
                </div>
              </div>
            )}

            <div
              style={{
                padding: '16px',
                backgroundColor: '#f5f5f5',
                borderRadius: '4px',
                maxHeight: '500px',
                overflow: 'auto'
              }}
            >
              <ReactMarkdown>{selectedIdea.content}</ReactMarkdown>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default Ideas
