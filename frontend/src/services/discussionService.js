/**
 * 讨论（交流广场）相关API服务
 */
import request from './request'

const discussionService = {
  /**
   * 创建讨论
   * @param {object} discussionData - 讨论数据
   * @param {string} discussionData.content - 讨论内容
   * @param {boolean} discussionData.is_anonymous - 是否匿名（可选，默认false）
   * @param {number} discussionData.parent_id - 父讨论ID（回复时使用，可选）
   * @returns {Promise}
   */
  createDiscussion: async (discussionData) => {
    return request.post('/discussions/', discussionData)
  },

  /**
   * 获取讨论列表
   * @param {object} params - 查询参数
   * @param {number} params.page - 页码（默认1）
   * @param {number} params.page_size - 每页数量（默认10）
   * @param {string} params.sort_order - 排序方向（newest=最新, oldest=最早, hottest=最热门）
   * @param {boolean} params.show_hidden - 是否显示隐藏内容（仅管理员）
   * @returns {Promise}
   */
  getDiscussions: async (params = {}) => {
    const queryParams = {
      page: params.page || 1,
      page_size: params.page_size || 10,
      sort_order: params.sort_order || 'newest',
      show_hidden: params.show_hidden || false
    }
    return request.get('/discussions/', { params: queryParams })
  },

  /**
   * 获取单个讨论详情
   * @param {number} discussionId - 讨论ID
   * @returns {Promise}
   */
  getDiscussion: async (discussionId) => {
    return request.get(`/discussions/${discussionId}`)
  },

  /**
   * 更新讨论内容
   * @param {number} discussionId - 讨论ID
   * @param {object} discussionData - 更新的讨论数据
   * @param {string} discussionData.content - 讨论内容
   * @returns {Promise}
   */
  updateDiscussion: async (discussionId, discussionData) => {
    return request.put(`/discussions/${discussionId}`, discussionData)
  },

  /**
   * 删除讨论
   * @param {number} discussionId - 讨论ID
   * @returns {Promise}
   */
  deleteDiscussion: async (discussionId) => {
    return request.delete(`/discussions/${discussionId}`)
  },

  /**
   * 点赞讨论
   * @param {number} discussionId - 讨论ID
   * @returns {Promise}
   */
  likeDiscussion: async (discussionId) => {
    return request.post(`/discussions/${discussionId}/like`)
  },

  /**
   * 取消点赞讨论
   * @param {number} discussionId - 讨论ID
   * @returns {Promise}
   */
  unlikeDiscussion: async (discussionId) => {
    return request.delete(`/discussions/${discussionId}/like`)
  },

  /**
   * 收藏讨论
   * @param {number} discussionId - 讨论ID
   * @returns {Promise}
   */
  favoriteDiscussion: async (discussionId) => {
    return request.post(`/discussions/${discussionId}/favorite`)
  },

  /**
   * 取消收藏讨论
   * @param {number} discussionId - 讨论ID
   * @returns {Promise}
   */
  unfavoriteDiscussion: async (discussionId) => {
    return request.delete(`/discussions/${discussionId}/favorite`)
  },

  /**
   * 获取收藏的讨论列表
   * @param {object} params - 查询参数
   * @param {number} params.page - 页码（默认1）
   * @param {number} params.page_size - 每页数量（默认10）
   * @returns {Promise}
   */
  getFavorites: async (params = {}) => {
    const queryParams = {
      page: params.page || 1,
      page_size: params.page_size || 10
    }
    return request.get('/discussions/favorites', { params: queryParams })
  },

  /**
   * 举报讨论
   * @param {number} discussionId - 讨论ID
   * @param {object} reportData - 举报数据
   * @param {string} reportData.reason - 举报原因
   * @returns {Promise}
   */
  reportDiscussion: async (discussionId, reportData) => {
    return request.post(`/discussions/${discussionId}/report`, reportData)
  },

  /**
   * 获取举报列表（管理员）
   * @param {object} params - 查询参数
   * @param {string} params.status - 状态筛选（pending/handled/rejected）
   * @param {number} params.page - 页码
   * @param {number} params.page_size - 每页数量
   * @returns {Promise}
   */
  getReports: async (params = {}) => {
    return request.get('/discussions/reports', { params })
  },

  /**
   * 处理举报（管理员）
   * @param {number} reportId - 举报ID
   * @param {object} handleData - 处理数据
   * @param {string} handleData.status - 处理状态（handled/rejected）
   * @returns {Promise}
   */
  handleReport: async (reportId, handleData) => {
    return request.put(`/discussions/reports/${reportId}/handle`, handleData)
  },

  /**
   * 隐藏讨论（管理员）
   * @param {number} discussionId - 讨论ID
   * @returns {Promise}
   */
  hideDiscussion: async (discussionId) => {
    return request.put(`/discussions/${discussionId}/hide`)
  },

  /**
   * 取消隐藏讨论（管理员）
   * @param {number} discussionId - 讨论ID
   * @returns {Promise}
   */
  unhideDiscussion: async (discussionId) => {
    return request.put(`/discussions/${discussionId}/unhide`)
  },

  /**
   * 获取匿名设置
   * @returns {Promise}
   */
  getAnonymousSetting: async () => {
    return request.get('/discussions/admin/settings/anonymous')
  },

  /**
   * 更新匿名设置（管理员）
   * @param {boolean} allowAnonymous - 是否允许匿名
   * @returns {Promise}
   */
  updateAnonymousSetting: async (allowAnonymous) => {
    return request.put('/discussions/admin/settings/anonymous', {
      setting_value: allowAnonymous ? 'true' : 'false'
    })
  }
}

export default discussionService
