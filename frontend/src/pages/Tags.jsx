import React, { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  message,
  Popconfirm
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TagOutlined
} from '@ant-design/icons'
import { SketchPicker } from 'react-color'
import tagService from '../services/tagService'

export default function Tags() {
  const [form] = Form.useForm()
  const [tags, setTags] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingTag, setEditingTag] = useState(null)
  const [selectedColor, setSelectedColor] = useState('#1890ff')

  // 加载标签列表
  useEffect(() => {
    loadTags()
  }, [])

  const loadTags = async () => {
    setLoading(true)
    try {
      const response = await tagService.getTags()
      if (response.code === 200) {
        setTags(response.data.tags)
      } else {
        message.error(response.message || '加载标签列表失败')
      }
    } catch (error) {
      message.error('加载标签列表失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 打开创建/编辑对话框
  const showModal = (tag = null) => {
    setEditingTag(tag)
    if (tag) {
      form.setFieldsValue({
        name: tag.name,
        color: tag.color
      })
      setSelectedColor(tag.color)
    } else {
      form.resetFields()
      setSelectedColor('#1890ff')
    }
    setModalVisible(true)
  }

  // 关闭对话框
  const handleCancel = () => {
    setModalVisible(false)
    setEditingTag(null)
    form.resetFields()
  }

  // 提交表单
  const handleSubmit = async (values) => {
    try {
      const tagData = {
        name: values.name,
        color: selectedColor
      }

      let response
      if (editingTag) {
        response = await tagService.updateTag(editingTag.id, tagData)
      } else {
        response = await tagService.createTag(tagData)
      }

      if (response.code === 200) {
        message.success(editingTag ? '标签更新成功' : '标签创建成功')
        handleCancel()
        loadTags()
      } else {
        message.error(response.message || '操作失败')
      }
    } catch (error) {
      message.error('操作失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  // 删除标签
  const handleDelete = async (tagId) => {
    try {
      const response = await tagService.deleteTag(tagId)
      if (response.code === 200) {
        message.success('标签删除成功')
        loadTags()
      } else {
        message.error(response.message || '标签删除失败')
      }
    } catch (error) {
      message.error('标签删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  // 表格列定义
  const columns = [
    {
      title: '标签名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Tag color={record.color} style={{ fontSize: '14px', padding: '4px 12px' }}>
          {text}
        </Tag>
      ),
    },
    {
      title: '颜色',
      dataIndex: 'color',
      key: 'color',
      width: '120px',
      render: (color) => (
        <Space>
          <div
            style={{
              width: '24px',
              height: '24px',
              backgroundColor: color,
              border: '1px solid #d9d9d9',
              borderRadius: '4px'
            }}
          />
          <span>{color}</span>
        </Space>
      ),
    },
    {
      title: '论文数量',
      dataIndex: 'paper_count',
      key: 'paper_count',
      width: '100px',
      align: 'center',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: '180px',
      render: (date) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: '150px',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => showModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除"
            description={`确定要删除标签"${record.name}"吗？这会移除该标签与所有论文的关联。`}
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <TagOutlined />
            <span>标签管理</span>
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => showModal()}
          >
            创建标签
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={tags}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个标签`,
          }}
        />
      </Card>

      {/* 创建/编辑标签对话框 */}
      <Modal
        title={editingTag ? '编辑标签' : '创建标签'}
        open={modalVisible}
        onCancel={handleCancel}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="标签名称"
            name="name"
            rules={[
              { required: true, message: '请输入标签名称' },
              { max: 50, message: '标签名称最多50个字符' }
            ]}
          >
            <Input placeholder="请输入标签名称" />
          </Form.Item>

          <Form.Item label="标签颜色">
            <div style={{ marginBottom: 12 }}>
              <Tag color={selectedColor} style={{ fontSize: '14px', padding: '4px 12px' }}>
                {form.getFieldValue('name') || '标签预览'}
              </Tag>
            </div>
            <SketchPicker
              color={selectedColor}
              onChange={(color) => setSelectedColor(color.hex)}
              disableAlpha
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingTag ? '更新' : '创建'}
              </Button>
              <Button onClick={handleCancel}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
