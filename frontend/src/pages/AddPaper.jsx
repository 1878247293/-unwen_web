import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Form,
  Input,
  InputNumber,
  Button,
  Upload,
  message,
  Card,
  Select,
  Space,
  Tag,
  Switch
} from 'antd'
import { UploadOutlined, SaveOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import paperService from '../services/paperService'
import tagService from '../services/tagService'

const { TextArea } = Input
const { Option } = Select

const AddPaper = () => {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [fileUploading, setFileUploading] = useState(false)
  const [uploadedFilePath, setUploadedFilePath] = useState(null)
  const [availableTags, setAvailableTags] = useState([])
  const [loadingTags, setLoadingTags] = useState(false)

  // 加载标签列表
  useEffect(() => {
    loadTags()
  }, [])

  const loadTags = async () => {
    setLoadingTags(true)
    try {
      const response = await tagService.getTags()
      if (response.code === 200) {
        setAvailableTags(response.data.tags || [])
      }
    } catch (error) {
      console.error('加载标签失败:', error)
    } finally {
      setLoadingTags(false)
    }
  }

  // 处理文件上传
  const handleFileUpload = async (info) => {
    const { file } = info

    // 只在开始上传时处理
    if (file.status !== 'uploading' && !fileUploading) {
      setFileUploading(true)

      try {
        const response = await paperService.uploadFile(file.originFileObj || file)

        if (response.code === 200) {
          message.success('PDF文件上传成功')
          setUploadedFilePath(response.data.filepath)
        } else {
          message.error(response.message || 'PDF文件上传失败')
        }
      } catch (error) {
        message.error('PDF文件上传失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        setFileUploading(false)
      }
    }
  }

  // 提交表单
  const handleSubmit = async (values) => {
    setLoading(true)

    try {
      // 准备提交数据
      const paperData = {
        title: values.title,
        authors: values.authors || null,
        journal: values.journal || null,
        year: values.year || null,
        volume: values.volume || null,
        issue: values.issue || null,
        pages: values.pages || null,
        doi: values.doi || null,
        arxiv_id: values.arxiv_id || null,
        abstract: values.abstract || null,
        keywords: values.keywords || null,
        url: values.url || null,
        reading_status: values.reading_status || 'unread',
        is_shared: values.is_shared || false,  // 添加is_shared字段
        pdf_path: uploadedFilePath
      }

      const response = await paperService.createPaper(paperData)

      if (response.code === 200) {
        const paperId = response.data.id

        // 如果选择了标签，添加标签关联
        if (values.tags && values.tags.length > 0) {
          try {
            await tagService.addTagsToPaper(paperId, values.tags)
          } catch (error) {
            console.error('添加标签失败:', error)
            message.warning('论文创建成功，但部分标签添加失败')
          }
        }

        message.success('论文添加成功')
        navigate('/papers')
      } else {
        message.error(response.message || '论文添加失败')
      }
    } catch (error) {
      message.error('论文添加失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1000px', margin: '0 auto' }}>
      <Card
        title="添加论文"
        extra={
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/papers')}
          >
            返回列表
          </Button>
        }
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            reading_status: 'unread'
          }}
        >
          {/* 基本信息 */}
          <Form.Item
            label="论文标题"
            name="title"
            rules={[{ required: true, message: '请输入论文标题' }]}
          >
            <Input placeholder="请输入论文标题" />
          </Form.Item>

          <Form.Item
            label="作者"
            name="authors"
            tooltip="多个作者请用逗号分隔"
          >
            <Input placeholder="例如: 张三, 李四, 王五" />
          </Form.Item>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              label="期刊/会议"
              name="journal"
              style={{ flex: 1, minWidth: '300px' }}
            >
              <Input placeholder="期刊或会议名称" />
            </Form.Item>

            <Form.Item
              label="年份"
              name="year"
            >
              <InputNumber
                min={1900}
                max={2100}
                style={{ width: '120px' }}
                placeholder="年份"
              />
            </Form.Item>
          </Space>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              label="卷号"
              name="volume"
            >
              <Input style={{ width: '100px' }} placeholder="卷号" />
            </Form.Item>

            <Form.Item
              label="期号"
              name="issue"
            >
              <Input style={{ width: '100px' }} placeholder="期号" />
            </Form.Item>

            <Form.Item
              label="页码"
              name="pages"
            >
              <Input style={{ width: '150px' }} placeholder="例如: 1-10" />
            </Form.Item>
          </Space>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              label="DOI"
              name="doi"
              style={{ flex: 1, minWidth: '250px' }}
            >
              <Input placeholder="例如: 10.1234/example" />
            </Form.Item>

            <Form.Item
              label="arXiv ID"
              name="arxiv_id"
              style={{ flex: 1, minWidth: '250px' }}
            >
              <Input placeholder="例如: 2301.12345" />
            </Form.Item>
          </Space>

          <Form.Item
            label="摘要"
            name="abstract"
          >
            <TextArea
              rows={6}
              placeholder="请输入论文摘要"
            />
          </Form.Item>

          <Form.Item
            label="关键词"
            name="keywords"
            tooltip="多个关键词请用逗号分隔"
          >
            <Input placeholder="例如: 深度学习, 自然语言处理, 机器翻译" />
          </Form.Item>

          <Form.Item
            label="论文链接"
            name="url"
          >
            <Input placeholder="论文在线链接" />
          </Form.Item>

          <Form.Item
            label="阅读状态"
            name="reading_status"
          >
            <Select>
              <Option value="unread">未读</Option>
              <Option value="reading">在读</Option>
              <Option value="read">已读</Option>
            </Select>
          </Form.Item>

          {/* 标签选择 */}
          <Form.Item
            label="标签"
            name="tags"
            tooltip="可选择多个标签，帮助分类管理论文"
          >
            <Select
              mode="multiple"
              placeholder="请选择标签"
              loading={loadingTags}
              allowClear
              tagRender={(props) => {
                const { label, value, closable, onClose } = props
                const tag = availableTags.find(t => t.id === value)
                return (
                  <Tag
                    color={tag?.color || '#1890ff'}
                    closable={closable}
                    onClose={onClose}
                    style={{ marginRight: 3 }}
                  >
                    {label}
                  </Tag>
                )
              }}
            >
              {availableTags.map(tag => (
                <Option key={tag.id} value={tag.id}>
                  <Tag color={tag.color}>{tag.name}</Tag>
                </Option>
              ))}
            </Select>
          </Form.Item>

          {/* 是否共享开关 */}
          <Form.Item
            label="是否共享"
            name="is_shared"
            valuePropName="checked"
            tooltip="共享后，所有用户都可以查看此论文；不共享则仅自己和管理员可见"
            initialValue={false}
          >
            <Switch
              checkedChildren="共享"
              unCheckedChildren="私人"
            />
          </Form.Item>

          {/* PDF上传 */}
          <Form.Item
            label="PDF文件"
            tooltip="支持上传PDF格式，最大50MB"
          >
            <Upload
              accept=".pdf"
              maxCount={1}
              beforeUpload={() => false}
              onChange={handleFileUpload}
            >
              <Button
                icon={<UploadOutlined />}
                loading={fileUploading}
              >
                {uploadedFilePath ? '重新上传PDF' : '上传PDF'}
              </Button>
            </Upload>
            {uploadedFilePath && (
              <div style={{ marginTop: '8px', color: '#52c41a' }}>
                ✓ PDF已上传
              </div>
            )}
          </Form.Item>

          {/* 提交按钮 */}
          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={loading}
              >
                保存
              </Button>
              <Button onClick={() => navigate('/papers')}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default AddPaper
