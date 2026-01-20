import { useState } from 'react'
import { Form, Input, Button, Card, message } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { useNavigate, Link } from 'react-router-dom'
import { authService } from '../services/authService'
import './Login.css'

export default function Register() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onFinish = async (values) => {
    if (values.password !== values.confirmPassword) {
      message.error('两次输入的密码不一致！')
      return
    }

    setLoading(true)
    try {
      const { confirmPassword, ...registerData } = values
      const response = await authService.register(registerData)

      message.success('注册成功！请等待管理员审核')
      setTimeout(() => {
        navigate('/login')
      }, 1500)
    } catch (error) {
      console.error('注册失败:', error)

      // 显示友好的错误提示
      if (error.response?.status === 400) {
        const detail = error.response?.data?.detail || ''
        if (detail.includes('用户名')) {
          message.error('用户名已被使用，请换一个')
        } else if (detail.includes('邮箱')) {
          message.error('该邮箱已被注册')
        } else if (detail.includes('验证')) {
          message.error('请检查输入格式是否正确')
        } else {
          message.error(detail || '注册失败，请检查输入')
        }
      } else if (error.response?.data?.detail) {
        message.error(error.response.data.detail)
      } else {
        message.error('注册失败，请检查网络连接或稍后重试')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      {/* 背景装饰元素 */}
      <div className="floating-shapes">
        <div className="shape"></div>
        <div className="shape"></div>
        <div className="shape"></div>
      </div>

      <Card className="login-card" title="注册 - 科研论文管理系统">
        <Form
          name="register"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名!' },
              { min: 3, message: '用户名至少3个字符!' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱!' },
              { type: 'email', message: '请输入有效的邮箱地址!' }
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="邮箱"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码!' },
              { min: 6, message: '密码至少6个字符!' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            rules={[{ required: true, message: '请确认密码!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="确认密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              注册
            </Button>
          </Form.Item>

          <div className="login-footer">
            已有账号？<Link to="/login">立即登录</Link>
          </div>
        </Form>
      </Card>
    </div>
  )
}
