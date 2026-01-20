import axios from 'axios'
import { message } from 'antd'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const authStorage = localStorage.getItem('auth-storage')
    console.log('🔍 [Request Interceptor] authStorage:', authStorage ? 'exists' : 'not found')

    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage)
        console.log('🔍 [Request Interceptor] parsed storage:', parsed)

        const { token } = parsed.state
        console.log('🔍 [Request Interceptor] token:', token ? `${token.substring(0, 20)}...` : 'not found')

        if (token) {
          config.headers.Authorization = `Bearer ${token}`
          console.log('✅ [Request Interceptor] Authorization header set')
        } else {
          console.warn('⚠️ [Request Interceptor] No token in state')
        }
      } catch (error) {
        console.error('❌ [Request Interceptor] Error parsing auth storage:', error)
      }
    } else {
      console.warn('⚠️ [Request Interceptor] No auth storage found')
    }

    console.log('🚀 [Request] ' + config.method.toUpperCase() + ' ' + config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 统一处理响应
    if (res.success === false) {
      message.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  (error) => {
    // 检查是否是认证相关的请求（登录、注册），这些请求的错误由页面自己处理
    const isAuthRequest = error.config?.url?.includes('/auth/')

    if (error.response) {
      // 对于认证请求，不显示通用错误消息，直接抛出错误
      if (isAuthRequest) {
        return Promise.reject(error)
      }

      // 对于其他请求，显示通用错误消息
      switch (error.response.status) {
        case 401:
          message.error('未授权，请重新登录')
          // 清除token并跳转到登录页
          localStorage.removeItem('auth-storage')
          window.location.href = '/login'
          break
        case 403:
          message.error('没有权限访问')
          break
        case 404:
          message.error('请求的资源不存在')
          break
        case 500:
          message.error('服务器错误')
          break
        default:
          message.error(error.response.data?.detail || '请求失败')
      }
    } else {
      // 网络错误
      if (!isAuthRequest) {
        message.error('网络错误，请检查网络连接')
      }
    }
    return Promise.reject(error)
  }
)

export default request
