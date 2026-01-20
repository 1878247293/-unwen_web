/**
 * 管理员相关API服务
 */
import request from './request'

const adminService = {
  /**
   * 获取管理员统计概览
   * @returns {Promise}
   */
  getOverview: () => {
    return request.get('/stats/admin/overview')
  },

  /**
   * 获取用户增长趋势
   * @param {number} days - 统计天数，默认30天
   * @returns {Promise}
   */
  getUserGrowth: (days = 30) => {
    return request.get('/stats/admin/user-growth', {
      params: { days }
    })
  }
}

export default adminService
