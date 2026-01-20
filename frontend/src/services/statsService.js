/**
 * 统计相关的API服务
 */

import request from './request'

const statsService = {
  /**
   * 获取Dashboard统计数据
   * @returns {Promise}
   */
  getDashboardStats: async () => {
    return request.get('/stats/dashboard')
  },

  /**
   * 获取阅读进度统计
   * @returns {Promise}
   */
  getReadingProgress: async () => {
    return request.get('/stats/reading-progress')
  }
}

export default statsService
