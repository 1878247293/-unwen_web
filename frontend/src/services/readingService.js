/**
 * 阅读进度和历史相关的API服务
 */

import request from './request'

const readingService = {
  /**
   * 更新论文阅读进度
   * @param {number} paperId - 论文ID
   * @param {number} progress - 阅读进度(0-100)
   * @returns {Promise}
   */
  updateProgress: async (paperId, progress) => {
    return request.put(`/reading/papers/${paperId}/progress`, {
      reading_progress: progress
    })
  },

  /**
   * 创建阅读会话记录
   * @param {number} paperId - 论文ID
   * @param {Object} sessionData - 会话数据
   * @returns {Promise}
   */
  createSession: async (paperId, sessionData) => {
    return request.post(`/reading/papers/${paperId}/sessions`, sessionData)
  },

  /**
   * 获取论文的阅读历史
   * @param {number} paperId - 论文ID
   * @returns {Promise}
   */
  getPaperHistory: async (paperId) => {
    return request.get(`/reading/papers/${paperId}/history`)
  },

  /**
   * 获取用户阅读统计
   * @returns {Promise}
   */
  getReadingStats: async () => {
    return request.get('/reading/stats')
  },

  /**
   * 获取所有论文的阅读统计
   * @returns {Promise}
   */
  getPapersStats: async () => {
    return request.get('/reading/papers/stats')
  }
}

export default readingService
