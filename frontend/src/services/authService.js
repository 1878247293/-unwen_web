import request from './request'

export const authService = {
  // 用户注册
  register: (data) => {
    return request.post('/auth/register', data)
  },

  // 用户登录
  login: (data) => {
    return request.post('/auth/login', data)
  },

  // 用户登出
  logout: () => {
    return request.post('/auth/logout')
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    return request.get('/users/me')
  },

  // 更新用户信息
  updateUser: (data) => {
    return request.put('/users/me', data)
  },

  // 修改密码
  updatePassword: (data) => {
    return request.put('/users/me/password', data)
  },

  // 获取用户统计信息
  getUserStats: () => {
    return request.get('/users/me/stats')
  },
}
