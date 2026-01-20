import { useState } from 'react'
import { Form, Input, Button, Card, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authService } from '../services/authService'
import './Login.css'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const onFinish = async (values) => {
    setLoading(true)
    try {
      const response = await authService.login(values)
      console.log('🔍 [Login] Full response:', response)
      console.log('🔍 [Login] response.data:', response.data)

      const { access_token, user } = response.data
      console.log('🔍 [Login] access_token:', access_token ? `${access_token.substring(0, 20)}...` : 'not found')
      console.log('🔍 [Login] user:', user)

      // 保存到状态管理
      login(access_token, user)
      console.log('✅ [Login] Token saved to store')

      // 验证是否保存成功
      const authStorage = localStorage.getItem('auth-storage')
      console.log('🔍 [Login] Verification - localStorage auth-storage:', authStorage ? 'exists' : 'not found')
      if (authStorage) {
        const parsed = JSON.parse(authStorage)
        console.log('🔍 [Login] Verification - parsed:', parsed)
      }

      message.success('登录成功！')
      navigate('/')
    } catch (error) {
      console.error('❌ [Login] 登录失败:', error)

      // 显示友好的错误提示
      if (error.response?.status === 401) {
        // 显示后端返回的具体错误信息（用户名不存在或密码错误）
        const detail = error.response?.data?.detail || '用户名或密码错误，请重试'
        message.error(detail)
      } else if (error.response?.status === 429) {
        // 账号锁定/冷却期
        const detail = error.response?.data?.detail || '操作过于频繁，请稍后再试'
        message.error(detail, 5) // 显示5秒，因为是重要提示
      } else if (error.response?.status === 403) {
        const detail = error.response?.data?.detail || ''
        if (detail.includes('待审核')) {
          message.warning('您的账号正在审核中，请等待管理员激活')
        } else if (detail.includes('禁用')) {
          message.error('您的账号已被禁用，请联系管理员')
        } else {
          message.error('账号状态异常，请联系管理员')
        }
      } else if (error.response?.data?.detail) {
        message.error(error.response.data.detail)
      } else {
        message.error('登录失败，请检查网络连接或稍后重试')
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

      <Card className="login-card" title="登录 - 科研论文管理系统">
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名或邮箱!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名或邮箱"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              登录
            </Button>
          </Form.Item>

          <div className="login-footer">
            还没有账号？<Link to="/register">立即注册</Link>
          </div>
        </Form>
      </Card>
    </div>
  )
}
