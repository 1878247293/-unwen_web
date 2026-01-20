/**
 * 通知管理服务
 */
import request from './request'

const notificationService = {
  /**
   * 获取通知列表
   * @param {Object} params - 查询参数
   * @param {boolean} params.is_read - 筛选已读/未读
   * @param {number} params.page - 页码
   * @param {number} params.page_size - 每页数量
   * @returns {Promise}
   */
  getNotifications: async (params = {}) => {
    return request.get('/notifications/', { params })
  },

  /**
   * 获取未读通知数量
   * @returns {Promise}
   */
  getUnreadCount: async () => {
    return request.get('/notifications/unread-count')
  },

  /**
   * 标记通知为已读
   * @param {number} notificationId - 通知ID
   * @returns {Promise}
   */
  markAsRead: async (notificationId) => {
    return request.put(`/notifications/${notificationId}/read`)
  },

  /**
   * 标记所有通知为已读
   * @returns {Promise}
   */
  markAllAsRead: async () => {
    return request.put('/notifications/read-all')
  },

  /**
   * 删除通知
   * @param {number} notificationId - 通知ID
   * @returns {Promise}
   */
  deleteNotification: async (notificationId) => {
    return request.delete(`/notifications/${notificationId}`)
  }
}

export default notificationService
