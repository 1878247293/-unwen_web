import React, { lazy, Suspense, useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Descriptions,
  Button,
  Space,
  Tag,
  Spin,
  message,
  Modal,
  Slider,
  Progress,
  Tabs,
  List,
  Empty,
  Popconfirm
} from 'antd'
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  FileTextOutlined,
  DownloadOutlined,
  PlusOutlined,
  FormOutlined,
  PrinterOutlined,
  ExportOutlined
} from '@ant-design/icons'
import paperService from '../services/paperService'
import readingService from '../services/readingService'
import noteService from '../services/noteService'
import { useAuthStore } from '../store/authStore'
import CommentList from '../components/CommentList'

// 懒加载重型组件（Markdown编辑器）
const NoteEditor = lazy(() => import('../components/NoteEditor'))

const PaperDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const [paper, setPaper] = useState(null)
  const [loading, setLoading] = useState(true)
  const [updatingProgress, setUpdatingProgress] = useState(false)
  const [activeTab, setActiveTab] = useState('info')
  const [notes, setNotes] = useState([])
  const [notesLoading, setNotesLoading] = useState(false)
  const [editingNote, setEditingNote] = useState(null)
  const [showNoteEditor, setShowNoteEditor] = useState(false)

  // 加载论文详情
  useEffect(() => {
    loadPaperDetail()
  }, [id])

  const loadPaperDetail = async () => {
    setLoading(true)
    try {
      const response = await paperService.getPaper(id)

      if (response.code === 200) {
        setPaper(response.data)
      } else {
        message.error(response.message || '加载论文详情失败')
        navigate('/papers')
      }
    } catch (error) {
      message.error('加载论文详情失败: ' + (error.response?.data?.detail || error.message))
      navigate('/papers')
    } finally {
      setLoading(false)
    }
  }

  // 加载笔记列表
  const loadNotes = async () => {
    setNotesLoading(true)
    try {
      const response = await noteService.getPaperNotes(id)
      if (response.code === 200) {
        setNotes(response.data.notes || [])
      } else {
        message.error(response.message || '加载笔记失败')
      }
    } catch (error) {
      message.error('加载笔记失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setNotesLoading(false)
    }
  }

  // 切换标签时加载数据
  useEffect(() => {
    if (activeTab === 'notes' && notes.length === 0) {
      loadNotes()
    }
  }, [activeTab])

  // 创建笔记
  const handleCreateNote = () => {
    setEditingNote(null)
    setShowNoteEditor(true)
  }

  // 编辑笔记
  const handleEditNote = (note) => {
    setEditingNote(note)
    setShowNoteEditor(true)
  }

  // 保存笔记后的回调
  const handleNoteSaved = () => {
    setShowNoteEditor(false)
    setEditingNote(null)
    loadNotes()
  }

  // 删除笔记
  const handleDeleteNote = async (noteId) => {
    try {
      const response = await noteService.deleteNote(noteId)
      if (response.code === 200) {
        message.success('笔记删除成功')
        loadNotes()
      } else {
        message.error(response.message || '删除笔记失败')
      }
    } catch (error) {
      message.error('删除笔记失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  // 笔记类型标签颜色
  const getNoteTypeTag = (type) => {
    const typeMap = {
      general: { color: 'default', text: '一般笔记' },
      summary: { color: 'blue', text: '总结' },
      method: { color: 'green', text: '方法' },
      conclusion: { color: 'purple', text: '结论' },
      innovation: { color: 'orange', text: '创新点' },
      limitation: { color: 'red', text: '局限性' },
      thinking: { color: 'cyan', text: '个人思考' }
    }
    const config = typeMap[type] || { color: 'default', text: type }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  // 更新阅读进度
  const handleProgressChange = async (value) => {
    setUpdatingProgress(true)
    try {
      const response = await readingService.updateProgress(id, value)

      if (response.code === 200) {
        setPaper(prev => ({
          ...prev,
          reading_progress: value,
          reading_status: response.data.reading_status
        }))
        message.success('阅读进度更新成功')
      } else {
        message.error(response.message || '更新阅读进度失败')
      }
    } catch (error) {
      message.error('更新阅读进度失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUpdatingProgress(false)
    }
  }

  // 删除论文
  const handleDelete = () => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除论文《${paper.title}》吗？此操作不可恢复。`,
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await paperService.deletePaper(id)

          if (response.code === 200) {
            message.success('论文删除成功')
            navigate('/papers')
          } else {
            message.error(response.message || '论文删除失败')
          }
        } catch (error) {
          message.error('论文删除失败: ' + (error.response?.data?.detail || error.message))
        }
      }
    })
  }

  // 阅读状态标签
  const getStatusTag = (status) => {
    const statusMap = {
      'unread': { color: 'default', text: '未读' },
      'reading': { color: 'processing', text: '在读' },
      'read': { color: 'success', text: '已读' }
    }
    const config = statusMap[status] || { color: 'default', text: status }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  // 打印功能
  const handlePrint = () => {
    window.print()
  }

  // 导出笔记为Markdown
  const handleExportNote = (noteId) => {
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

    // 下载笔记
    const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/notes/${noteId}/export?format=md`

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
        a.download = `note_${noteId}.md`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        message.success('笔记导出成功')
      })
      .catch(error => {
        message.error('导出笔记失败: ' + error.message)
      })
  }

  // 检查权限
  const canEdit = user?.role === 'admin' || paper?.created_by === user?.id

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!paper) {
    return null
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }} className="paper-detail-print">
      {/* 打印页眉 - 仅在打印时显示 */}
      <div className="print-header" style={{ display: 'none' }}>
        <h1>论文详情</h1>
        <p className="print-date">打印日期: {new Date().toLocaleString('zh-CN')}</p>
      </div>

      <Card
        title={paper.title}
        extra={
          <Space className="no-print">
            <Button
              icon={<PrinterOutlined />}
              onClick={handlePrint}
            >
              打印
            </Button>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/papers')}
            >
              返回列表
            </Button>
            {canEdit && (
              <>
                <Button
                  type="primary"
                  icon={<EditOutlined />}
                  onClick={() => navigate(`/papers/${id}/edit`)}
                >
                  编辑
                </Button>
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={handleDelete}
                >
                  删除
                </Button>
              </>
            )}
          </Space>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'info',
              label: '论文信息',
              children: (
                <Descriptions bordered column={{ xxl: 2, xl: 2, lg: 2, md: 1, sm: 1, xs: 1 }}>
                  <Descriptions.Item label="作者">
                    {paper.authors || '-'}
                  </Descriptions.Item>

                  <Descriptions.Item label="阅读状态">
                    {getStatusTag(paper.reading_status)}
                  </Descriptions.Item>

                  <Descriptions.Item label="阅读进度" span={2}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <Progress
                        percent={paper.reading_progress || 0}
                        style={{ flex: 1, maxWidth: '400px' }}
                        status={paper.reading_progress === 100 ? 'success' : 'active'}
                      />
                      {canEdit && (
                        <Slider
                          style={{ flex: 1, maxWidth: '200px' }}
                          min={0}
                          max={100}
                          value={paper.reading_progress || 0}
                          onChange={handleProgressChange}
                          disabled={updatingProgress}
                          tooltip={{ formatter: (value) => `${value}%` }}
                        />
                      )}
                    </div>
                  </Descriptions.Item>

                  <Descriptions.Item label="期刊/会议">
                    {paper.journal || '-'}
                  </Descriptions.Item>

                  <Descriptions.Item label="年份">
                    {paper.year || '-'}
                  </Descriptions.Item>

                  {paper.volume && (
                    <Descriptions.Item label="卷号">
                      {paper.volume}
                    </Descriptions.Item>
                  )}

                  {paper.issue && (
                    <Descriptions.Item label="期号">
                      {paper.issue}
                    </Descriptions.Item>
                  )}

                  {paper.pages && (
                    <Descriptions.Item label="页码">
                      {paper.pages}
                    </Descriptions.Item>
                  )}

                  {paper.doi && (
                    <Descriptions.Item label="DOI" span={2}>
                      <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer">
                        {paper.doi}
                      </a>
                    </Descriptions.Item>
                  )}

                  {paper.arxiv_id && (
                    <Descriptions.Item label="arXiv ID" span={2}>
                      <a href={`https://arxiv.org/abs/${paper.arxiv_id}`} target="_blank" rel="noopener noreferrer">
                        {paper.arxiv_id}
                      </a>
                    </Descriptions.Item>
                  )}

                  {paper.url && (
                    <Descriptions.Item label="论文链接" span={2}>
                      <a href={paper.url} target="_blank" rel="noopener noreferrer">
                        {paper.url}
                      </a>
                    </Descriptions.Item>
                  )}

                  {paper.keywords && (
                    <Descriptions.Item label="关键词" span={2}>
                      {paper.keywords.split(',').map((keyword, index) => (
                        <Tag key={index} style={{ margin: '2px' }}>
                          {keyword.trim()}
                        </Tag>
                      ))}
                    </Descriptions.Item>
                  )}

                  {paper.tags && paper.tags.length > 0 && (
                    <Descriptions.Item label="标签" span={2}>
                      {paper.tags.map((tag) => (
                        <Tag key={tag.id} color={tag.color} style={{ margin: '2px', cursor: 'pointer' }} onClick={() => navigate(`/papers?tag=${tag.id}`)}>
                          {tag.name}
                        </Tag>
                      ))}
                    </Descriptions.Item>
                  )}

                  {paper.abstract && (
                    <Descriptions.Item label="摘要" span={2}>
                      <div style={{ whiteSpace: 'pre-wrap' }}>
                        {paper.abstract}
                      </div>
                    </Descriptions.Item>
                  )}

                  {paper.pdf_path && (
                    <Descriptions.Item label="PDF文件" span={2}>
                      <Space>
                        <FileTextOutlined style={{ color: '#1890ff', fontSize: '20px' }} />
                        <span>已上传</span>
                        <Button
                          type="link"
                          icon={<DownloadOutlined />}
                          onClick={() => {
                            const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
                            const pdfUrl = `${apiUrl}/${paper.pdf_path.replace('data/', '')}`
                            window.open(pdfUrl, '_blank')
                          }}
                        >
                          查看PDF
                        </Button>
                        <Button
                          type="primary"
                          icon={<DownloadOutlined />}
                          onClick={() => {
                            const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
                            const pdfUrl = `${apiUrl}/${paper.pdf_path.replace('data/', '')}`
                            const link = document.createElement('a')
                            link.href = pdfUrl
                            link.download = `${paper.title}.pdf`
                            document.body.appendChild(link)
                            link.click()
                            document.body.removeChild(link)
                          }}
                        >
                          下载PDF
                        </Button>
                      </Space>
                    </Descriptions.Item>
                  )}

                  <Descriptions.Item label="创建者">
                    {paper.creator_name || '-'}
                  </Descriptions.Item>

                  <Descriptions.Item label="创建时间">
                    {new Date(paper.created_at).toLocaleString('zh-CN')}
                  </Descriptions.Item>

                  <Descriptions.Item label="更新时间" span={2}>
                    {new Date(paper.updated_at).toLocaleString('zh-CN')}
                  </Descriptions.Item>
                </Descriptions>
              )
            },
            {
              key: 'notes',
              label: '笔记',
              children: (
                <div>
                  {showNoteEditor ? (
                    <Suspense fallback={<Spin tip="加载编辑器..." style={{ display: 'block', margin: '50px auto' }} />}>
                      <NoteEditor
                        paperId={id}
                        note={editingNote}
                        onSave={handleNoteSaved}
                        onCancel={() => {
                          setShowNoteEditor(false)
                          setEditingNote(null)
                        }}
                      />
                    </Suspense>
                  ) : (
                    <>
                      <div style={{ marginBottom: '16px' }} className="no-print">
                        <Button
                          type="primary"
                          icon={<PlusOutlined />}
                          onClick={handleCreateNote}
                        >
                          创建笔记
                        </Button>
                      </div>
                      <Spin spinning={notesLoading}>
                        {notes.length === 0 ? (
                          <Empty description="暂无笔记，点击上方按钮创建第一条笔记" />
                        ) : (
                          <List
                            dataSource={notes}
                            renderItem={(note) => (
                              <List.Item
                                className="note-print"
                                actions={[
                                  <Button
                                    type="link"
                                    icon={<ExportOutlined />}
                                    onClick={() => handleExportNote(note.id)}
                                    className="no-print"
                                  >
                                    导出
                                  </Button>,
                                  <Button
                                    type="link"
                                    icon={<FormOutlined />}
                                    onClick={() => handleEditNote(note)}
                                    className="no-print"
                                  >
                                    编辑
                                  </Button>,
                                  <Popconfirm
                                    title="确定删除这条笔记吗？"
                                    onConfirm={() => handleDeleteNote(note.id)}
                                    okText="确定"
                                    cancelText="取消"
                                  >
                                    <Button type="link" danger icon={<DeleteOutlined />} className="no-print">
                                      删除
                                    </Button>
                                  </Popconfirm>
                                ]}
                              >
                                <List.Item.Meta
                                  title={
                                    <div className="note-print-header">
                                      <div className="note-print-title">
                                        {getNoteTypeTag(note.note_type)}
                                        {note.title || '无标题'}
                                      </div>
                                      <div className="note-print-meta">
                                        创建于 {new Date(note.created_at).toLocaleString('zh-CN')}
                                        {note.updated_at !== note.created_at &&
                                          ` · 更新于 ${new Date(note.updated_at).toLocaleString('zh-CN')}`
                                        }
                                      </div>
                                    </div>
                                  }
                                  description={
                                    <div className="note-print-content">
                                      {note.content}
                                    </div>
                                  }
                                />
                              </List.Item>
                            )}
                          />
                        )}
                      </Spin>
                    </>
                  )}
                </div>
              )
            },
            {
              key: 'comments',
              label: '评论',
              children: (
                <div>
                  <CommentList paperId={id} />
                </div>
              )
            }
          ]}
        />
      </Card>
    </div>
  )
}

export default PaperDetail
