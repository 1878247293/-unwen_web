/**
 * 评论相关API服务
 */
import request from './request'

const commentService = {
  /**
   * 为论文创建评论
   * @param {number} paperId - 论文ID
   * @param {object} commentData - 评论数据
   * @param {string} commentData.content - 评论内容
   * @param {number} commentData.parent_id - 父评论ID（回复时使用，可选）
   * @returns {Promise}
   */
  createComment: async (paperId, commentData) => {
    return request.post(`/comments/papers/${paperId}`, {
      ...commentData,
      paper_id: paperId
    })
  },

  /**
   * 获取论文的评论列表
   * @param {number} paperId - 论文ID
   * @param {object} params - 查询参数
   * @param {number} params.page - 页码（默认1）
   * @param {number} params.page_size - 每页数量（默认20）
   * @param {string} params.sort_order - 排序方向（desc=最新在前，asc=最早在前）
   * @returns {Promise}
   */
  getPaperComments: async (paperId, params = {}) => {
    const queryParams = {
      page: params.page || 1,
      page_size: params.page_size || 20,
      sort_order: params.sort_order || 'desc'
    }
    return request.get(`/comments/papers/${paperId}`, { params: queryParams })
  },

  /**
   * 获取单个评论详情
   * @param {number} commentId - 评论ID
   * @returns {Promise}
   */
  getComment: async (commentId) => {
    return request.get(`/comments/${commentId}`)
  },

  /**
   * 更新评论内容
   * @param {number} commentId - 评论ID
   * @param {object} commentData - 更新的评论数据
   * @param {string} commentData.content - 评论内容
   * @returns {Promise}
   */
  updateComment: async (commentId, commentData) => {
    return request.put(`/comments/${commentId}`, commentData)
  },

  /**
   * 删除评论
   * @param {number} commentId - 评论ID
   * @returns {Promise}
   */
  deleteComment: async (commentId) => {
    return request.delete(`/comments/${commentId}`)
  }
}

export default commentService
