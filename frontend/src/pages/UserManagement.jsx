/**
 * 用户管理页面（管理员）
 */
import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  Modal,
  Form,
  Select,
  message,
  Popconfirm,
  Badge
} from 'antd'
import {
  SearchOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  StopOutlined,
  EditOutlined,
  DeleteOutlined,
  KeyOutlined
} from '@ant-design/icons'
import userService from '../services/userService'

const { Search } = Input
const { Option } = Select

function UserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [passwordModalVisible, setPasswordModalVisible] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [form] = Form.useForm()
  const [passwordForm] = Form.useForm()

  // 加载用户列表
  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const response = await userService.getAllUsers({})
      if (response.code === 200) {
        setUsers(response.data)
      } else {
        message.error(response.message || '加载用户列表失败')
      }
    } catch (error) {
      message.error('加载用户列表失败: ' + (error.message || error))
    } finally {
      setLoading(false)
    }
  }

  // 过滤用户
  const filteredUsers = users.filter(user => {
    if (!searchText) return true
    return (
      user.username?.toLowerCase().includes(searchText.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchText.toLowerCase()) ||
      user.department?.toLowerCase().includes(searchText.toLowerCase())
    )
  })

  // 状态标签
  const getStatusTag = (status) => {
    const statusMap = {
      active: { color: 'success', icon: <CheckCircleOutlined />, text: '激活' },
      pending: { color: 'warning', icon: <ClockCircleOutlined />, text: '待审核' },
      disabled: { color: 'default', icon: <StopOutlined />, text: '禁用' }
    }
    const config = statusMap[status] || { color: 'default', icon: null, text: status }
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    )
  }

  // 角色标签
  const getRoleTag = (role) => {
    return role === 'admin' ? (
      <Tag color="red">管理员</Tag>
    ) : (
      <Tag color="blue">普通用户</Tag>
    )
  }

  // 更新用户状态
  const handleUpdateStatus = async (userId, newStatus) => {
    try {
      const response = await userService.updateUserStatus(userId, newStatus)
      if (response.code === 200) {
        message.success(response.message || '状态更新成功')
        loadUsers()
      } else {
        message.error(response.message || '状态更新失败')
      }
    } catch (error) {
      message.error('状态更新失败: ' + (error.message || error))
    }
  }

  // 打开编辑对话框
  const handleEdit = (user) => {
    setSelectedUser(user)
    form.setFieldsValue({
      role: user.role,
      status: user.status
    })
    setEditModalVisible(true)
  }

  // 提交编辑
  const handleEditSubmit = async () => {
    try {
      const values = await form.validateFields()

      // 更新角色
      if (values.role !== selectedUser.role) {
        const roleResponse = await userService.updateUserRole(selectedUser.id, values.role)
        if (roleResponse.code !== 200) {
          message.error(roleResponse.message || '角色更新失败')
          return
        }
      }

      // 更新状态
      if (values.status !== selectedUser.status) {
        const statusResponse = await userService.updateUserStatus(selectedUser.id, values.status)
        if (statusResponse.code !== 200) {
          message.error(statusResponse.message || '状态更新失败')
          return
        }
      }

      message.success('用户信息更新成功')
      setEditModalVisible(false)
      loadUsers()
    } catch (error) {
      if (error.errorFields) {
        message.error('请填写正确的信息')
      } else {
        message.error('更新失败: ' + (error.message || error))
      }
    }
  }

  // 打开重置密码对话框
  const handleResetPassword = (user) => {
    setSelectedUser(user)
    passwordForm.resetFields()
    setPasswordModalVisible(true)
  }

  // 提交密码重置
  const handlePasswordSubmit = async () => {
    try {
      const values = await passwordForm.validateFields()
      const response = await userService.resetUserPassword(
        selectedUser.id,
        values.newPassword
      )

      if (response.code === 200) {
        message.success('密码重置成功')
        setPasswordModalVisible(false)
        passwordForm.resetFields()
      } else {
        message.error(response.message || '密码重置失败')
      }
    } catch (error) {
      if (error.errorFields) {
        message.error('请填写正确的密码')
      } else {
        message.error('密码重置失败: ' + (error.message || error))
      }
    }
  }

  // 删除用户
  const handleDelete = async (userId) => {
    try {
      const response = await userService.deleteUser(userId)
      if (response.code === 200) {
        message.success(response.message || '用户删除成功')
        loadUsers()
      } else {
        message.error(response.message || '用户删除失败')
      }
    } catch (error) {
      message.error('用户删除失败: ' + (error.message || error))
    }
  }

  // 表格列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 120
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 100,
      render: (role) => getRoleTag(role)
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status)
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      width: 150,
      render: (text) => text || '-'
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => new Date(text).toLocaleString('zh-CN')
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 300,
      render: (_, record) => {
        const isAdminUser = record.username === 'admin'

        return (
          <Space>
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
              disabled={isAdminUser}
              title={isAdminUser ? 'admin用户信息不可修改' : '编辑用户'}
            >
              编辑
            </Button>
            <Button
              type="link"
              size="small"
              icon={<KeyOutlined />}
              onClick={() => handleResetPassword(record)}
              disabled={isAdminUser}
              title={isAdminUser ? 'admin用户密码不可修改' : '重置密码'}
            >
              重置密码
            </Button>
            {record.status === 'pending' && !isAdminUser && (
              <Button
                type="link"
                size="small"
                onClick={() => handleUpdateStatus(record.id, 'active')}
              >
                审核通过
              </Button>
            )}
            <Popconfirm
              title="确定要删除这个用户吗？"
              description="此操作将禁用该用户账号"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
              disabled={isAdminUser}
            >
              <Button
                type="link"
                danger
                size="small"
                icon={<DeleteOutlined />}
                disabled={isAdminUser}
                title={isAdminUser ? 'admin用户不可删除' : '删除用户'}
              >
                删除
              </Button>
            </Popconfirm>
          </Space>
        )
      }
    }
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <span>用户管理</span>
            <Badge count={filteredUsers.length} showZero />
          </Space>
        }
        extra={
          <Search
            placeholder="搜索用户名、邮箱或部门"
            allowClear
            enterButton={<SearchOutlined />}
            style={{ width: 300 }}
            onSearch={setSearchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        }
      >
        <Table
          columns={columns}
          dataSource={filteredUsers}
          loading={loading}
          rowKey="id"
          scroll={{ x: 1200 }}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
        />
      </Card>

      {/* 编辑用户对话框 */}
      <Modal
        title="编辑用户"
        open={editModalVisible}
        onOk={handleEditSubmit}
        onCancel={() => setEditModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item label="用户信息">
            <div>
              <div><strong>用户名:</strong> {selectedUser?.username}</div>
              <div><strong>邮箱:</strong> {selectedUser?.email}</div>
            </div>
          </Form.Item>

          <Form.Item
            label="角色"
            name="role"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select>
              <Option value="user">普通用户</Option>
              <Option value="admin">管理员</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="状态"
            name="status"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select>
              <Option value="pending">待审核</Option>
              <Option value="active">激活</Option>
              <Option value="disabled">禁用</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 重置密码对话框 */}
      <Modal
        title="重置用户密码"
        open={passwordModalVisible}
        onOk={handlePasswordSubmit}
        onCancel={() => setPasswordModalVisible(false)}
        okText="重置"
        cancelText="取消"
      >
        <Form
          form={passwordForm}
          layout="vertical"
        >
          <Form.Item label="用户信息">
            <div>
              <div><strong>用户名:</strong> {selectedUser?.username}</div>
              <div><strong>邮箱:</strong> {selectedUser?.email}</div>
            </div>
          </Form.Item>

          <Form.Item
            label="新密码"
            name="newPassword"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码长度至少6位' }
            ]}
          >
            <Input.Password placeholder="请输入新密码（至少6位）" />
          </Form.Item>

          <Form.Item
            label="确认密码"
            name="confirmPassword"
            dependencies={['newPassword']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('newPassword') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'))
                }
              })
            ]}
          >
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default UserManagement
