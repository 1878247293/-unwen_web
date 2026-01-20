/**
 * 想法管理API服务
 * 用于记录和管理用户的研究想法、灵感和思考
 */
import request from './request'

const ideasService = {
  /**
   * 创建想法
   * @param {Object} data - 想法数据
   * @param {string} data.title - 标题（可选）
   * @param {string} data.references - 参考文献（可选）
   * @param {string} data.content - 内容（必填）
   */
  createIdea: async (data) => {
    const params = new URLSearchParams()
    if (data.title) params.append('title', data.title)
    if (data.references) params.append('references', data.references)
    params.append('content', data.content)

    return request.post(`/ideas/?${params.toString()}`)
  },

  /**
   * 获取想法列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.page_size - 每页数量
   * @param {string} params.keyword - 搜索关键词
   */
  getIdeas: async (params = {}) => {
    return request.get('/ideas/', { params })
  },

  /**
   * 获取想法详情
   * @param {number} ideaId - 想法ID
   */
  getIdea: async (ideaId) => {
    return request.get(`/ideas/${ideaId}`)
  },

  /**
   * 更新想法
   * @param {number} ideaId - 想法ID
   * @param {Object} data - 更新数据
   * @param {string} data.title - 新标题（可选）
   * @param {string} data.references - 新参考文献（可选）
   * @param {string} data.content - 新内容（可选）
   */
  updateIdea: async (ideaId, data) => {
    const params = new URLSearchParams()
    if (data.title !== undefined) params.append('title', data.title)
    if (data.references !== undefined) params.append('references', data.references)
    if (data.content !== undefined) params.append('content', data.content)

    return request.put(`/ideas/${ideaId}?${params.toString()}`)
  },

  /**
   * 删除想法
   * @param {number} ideaId - 想法ID
   */
  deleteIdea: async (ideaId) => {
    return request.delete(`/ideas/${ideaId}`)
  }
}

export default ideasService
