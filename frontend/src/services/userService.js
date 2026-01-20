/**
 * 用户相关API服务
 */
import request from './request'

const userService = {
  /**
   * 获取当前用户信息
   * @returns {Promise}
   */
  getCurrentUser: () => {
    return request.get('/users/me')
  },

  /**
   * 更新当前用户信息
   * @param {object} data - 更新数据
   * @returns {Promise}
   */
  updateCurrentUser: (data) => {
    return request.put('/users/me', data)
  },

  /**
   * 修改密码
   * @param {object} data - 密码数据 {old_password, new_password}
   * @returns {Promise}
   */
  updatePassword: (data) => {
    return request.put('/users/me/password', data)
  },

  /**
   * 获取所有用户（管理员）
   * @param {object} params - 查询参数 {skip, limit}
   * @returns {Promise}
   */
  getAllUsers: (params = {}) => {
    return request.get('/users/', { params })
  },

  /**
   * 更新用户状态（管理员）
   * @param {number} userId - 用户ID
   * @param {string} status - 状态值 pending/active/disabled
   * @returns {Promise}
   */
  updateUserStatus: (userId, status) => {
    return request.put(`/users/${userId}/status`, null, {
      params: { status_value: status }
    })
  },

  /**
   * 更新用户角色（管理员）
   * @param {number} userId - 用户ID
   * @param {string} role - 角色值 user/admin
   * @returns {Promise}
   */
  updateUserRole: (userId, role) => {
    return request.put(`/users/${userId}/role`, { role })
  },

  /**
   * 重置用户密码（管理员）
   * @param {number} userId - 用户ID
   * @param {string} newPassword - 新密码
   * @returns {Promise}
   */
  resetUserPassword: (userId, newPassword) => {
    return request.post(`/users/${userId}/reset-password`, {
      new_password: newPassword
    })
  },

  /**
   * 删除用户（管理员）
   * @param {number} userId - 用户ID
   * @returns {Promise}
   */
  deleteUser: (userId) => {
    return request.delete(`/users/${userId}`)
  }
}

export default userService
