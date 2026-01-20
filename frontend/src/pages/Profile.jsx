import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  Form,
  Input,
  Button,
  Avatar,
  Upload,
  message,
  Tabs,
  Space,
  Descriptions,
  Spin
} from 'antd'
import {
  UserOutlined,
  UploadOutlined,
  LockOutlined,
  SaveOutlined
} from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import { authService } from '../services/authService'
import dayjs from 'dayjs'

const { TabPane } = Tabs

const Profile = () => {
  const { user, updateUser } = useAuthStore()
  const [form] = Form.useForm()
  const [passwordForm] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [statsLoading, setStatsLoading] = useState(false)

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        department: user.department
      })
    }
  }, [user, form])

  // 加载统计数据
  useEffect(() => {
    const loadStats = async () => {
      setStatsLoading(true)
      try {
        const response = await authService.getUserStats()
        if (response.code === 200) {
          setStats(response.data)
        }
      } catch (error) {
        console.error('获取统计信息失败', error)
      } finally {
        setStatsLoading(false)
      }
    }

    loadStats()
  }, [])

  const handleUpdateProfile = async (values) => {
    setLoading(true)
    try {
      // 调用API更新用户信息
      const response = await authService.updateUser(values)

      // 更新store中的用户信息
      updateUser(response.data)

      message.success('个人信息更新成功')
    } catch (error) {
      message.error('更新失败: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleChangePassword = async (values) => {
    setLoading(true)
    try {
      // 调用API修改密码
      await authService.updatePassword({
        old_password: values.old_password,
        new_password: values.new_password
      })

      message.success('密码修改成功')
      passwordForm.resetFields()
    } catch (error) {
      message.error('修改密码失败: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1000px', margin: '0 auto' }}>
      <Card title="个人中心">
        <Tabs defaultActiveKey="info">
          <TabPane tab="基本信息" key="info">
            <div style={{ display: 'flex', gap: '40px' }}>
              {/* 头像上传 */}
              <div style={{ textAlign: 'center' }}>
                <Avatar
                  size={120}
                  icon={<UserOutlined />}
                  src={user?.avatar}
                  style={{ marginBottom: '16px' }}
                />
                <Upload
                  showUploadList={false}
                  beforeUpload={() => false}
                  onChange={() => message.info('头像上传功能待实现')}
                >
                  <Button icon={<UploadOutlined />}>更换头像</Button>
                </Upload>
              </div>

              {/* 信息表单 */}
              <div style={{ flex: 1 }}>
                <Descriptions bordered column={1}>
                  <Descriptions.Item label="用户名">
                    {user?.username}
                  </Descriptions.Item>
                  <Descriptions.Item label="邮箱">
                    {user?.email}
                  </Descriptions.Item>
                  <Descriptions.Item label="角色">
                    {user?.role === 'admin' ? '管理员' : '普通用户'}
                  </Descriptions.Item>
                  <Descriptions.Item label="状态">
                    {user?.status === 'active' ? '正常' : user?.status}
                  </Descriptions.Item>
                  <Descriptions.Item label="部门">
                    {user?.department || '-'}
                  </Descriptions.Item>
                </Descriptions>

                <div style={{ marginTop: '24px' }}>
                  <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleUpdateProfile}
                  >
                    <Form.Item
                      label="部门"
                      name="department"
                    >
                      <Input placeholder="请输入部门" />
                    </Form.Item>

                    <Form.Item>
                      <Button
                        type="primary"
                        htmlType="submit"
                        icon={<SaveOutlined />}
                        loading={loading}
                      >
                        保存修改
                      </Button>
                    </Form.Item>
                  </Form>
                </div>
              </div>
            </div>
          </TabPane>

          <TabPane tab="修改密码" key="password">
            {user?.username === 'admin' ? (
              <Card>
                <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                  <LockOutlined style={{ fontSize: '48px', marginBottom: '16px', color: '#d9d9d9' }} />
                  <h3>admin用户的密码不可修改</h3>
                  <p>出于安全考虑，admin账户的密码无法通过此页面修改。</p>
                </div>
              </Card>
            ) : (
              <div style={{ maxWidth: '500px' }}>
                <Form
                  form={passwordForm}
                  layout="vertical"
                  onFinish={handleChangePassword}
                >
                  <Form.Item
                    label="当前密码"
                    name="old_password"
                    rules={[
                      { required: true, message: '请输入当前密码' }
                    ]}
                  >
                    <Input.Password
                      prefix={<LockOutlined />}
                      placeholder="请输入当前密码"
                    />
                  </Form.Item>

                  <Form.Item
                    label="新密码"
                    name="new_password"
                    rules={[
                      { required: true, message: '请输入新密码' },
                      { min: 6, message: '密码至少6位' }
                    ]}
                  >
                    <Input.Password
                      prefix={<LockOutlined />}
                      placeholder="请输入新密码（至少6位）"
                    />
                  </Form.Item>

                  <Form.Item
                    label="确认新密码"
                    name="confirm_password"
                    dependencies={['new_password']}
                    rules={[
                      { required: true, message: '请确认新密码' },
                      ({ getFieldValue }) => ({
                        validator(_, value) {
                          if (!value || getFieldValue('new_password') === value) {
                            return Promise.resolve()
                          }
                          return Promise.reject(new Error('两次输入的密码不一致'))
                        },
                      }),
                    ]}
                  >
                    <Input.Password
                      prefix={<LockOutlined />}
                      placeholder="请再次输入新密码"
                    />
                  </Form.Item>

                  <Form.Item>
                    <Space>
                      <Button
                        type="primary"
                        htmlType="submit"
                        icon={<SaveOutlined />}
                        loading={loading}
                      >
                        修改密码
                      </Button>
                      <Button onClick={() => passwordForm.resetFields()}>
                        重置
                      </Button>
                    </Space>
                  </Form.Item>
                </Form>
              </div>
            )}
          </TabPane>

          <TabPane tab="账号统计" key="stats">
            <Spin spinning={statsLoading}>
              <Descriptions bordered column={2}>
                <Descriptions.Item label="已添加论文">
                  {stats?.total_papers || 0} 篇
                </Descriptions.Item>
                <Descriptions.Item label="笔记数量">
                  {stats?.total_notes || 0} 条
                </Descriptions.Item>
                <Descriptions.Item label="标签数量">
                  {stats?.total_tags || 0} 个
                </Descriptions.Item>
                <Descriptions.Item label="想法数量">
                  {stats?.total_ideas || 0} 条
                </Descriptions.Item>
                <Descriptions.Item label="注册时间" span={2}>
                  {stats?.registration_date ? dayjs(stats.registration_date).format('YYYY-MM-DD HH:mm') : '-'}
                </Descriptions.Item>
              </Descriptions>
            </Spin>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  )
}

export default Profile
