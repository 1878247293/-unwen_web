/**
 * 改进建议相关的API服务
 */

import request from './request'

const suggestionService = {
  /**
   * 创建改进建议
   * @param {string} content - 建议内容
   * @returns {Promise}
   */
  createSuggestion: async (content) => {
    return await request.post('/suggestions/', null, {
      params: { content }
    })
  },

  /**
   * 获取建议列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getSuggestions: async (params = {}) => {
    return await request.get('/suggestions/', { params })
  },

  /**
   * 标记建议为已完成
   * @param {number} suggestionId - 建议ID
   * @returns {Promise}
   */
  completeSuggestion: async (suggestionId) => {
    return await request.put(`/suggestions/${suggestionId}/complete`)
  },

  /**
   * 取消完成标记
   * @param {number} suggestionId - 建议ID
   * @returns {Promise}
   */
  uncompleteSuggestion: async (suggestionId) => {
    return await request.put(`/suggestions/${suggestionId}/uncomplete`)
  },

  /**
   * 删除建议
   * @param {number} suggestionId - 建议ID
   * @returns {Promise}
   */
  deleteSuggestion: async (suggestionId) => {
    return await request.delete(`/suggestions/${suggestionId}`)
  }
}

export default suggestionService
