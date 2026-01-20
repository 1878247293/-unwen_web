/**
 * 网站收集服务
 *
 * 提供科研网站的CRUD操作
 */

import request from './request'

const websitesService = {
  /**
   * 创建网站
   * @param {Object} data - 网站数据
   * @param {string} data.name - 网站名称
   * @param {string} data.url - 网站URL
   * @param {string} [data.category] - 分类
   * @param {string} [data.description] - 描述
   * @param {boolean} [data.is_favorite] - 是否收藏
   */
  createWebsite(data) {
    const params = new URLSearchParams({
      name: data.name,
      url: data.url,
      is_favorite: data.is_favorite || false
    })

    if (data.category) params.append('category', data.category)
    if (data.description) params.append('description', data.description)

    return request.post(`/websites/?${params.toString()}`)
  },

  /**
   * 获取网站列表
   * @param {Object} params - 查询参数
   * @param {number} [params.page=1] - 页码
   * @param {number} [params.page_size=1000] - 每页数量
   * @param {string} [params.keyword] - 搜索关键词
   * @param {string} [params.category] - 分类筛选
   * @param {boolean} [params.is_favorite] - 是否只显示收藏
   */
  getWebsites(params = {}) {
    const queryParams = new URLSearchParams({
      page: params.page || 1,
      page_size: params.page_size || 1000
    })

    if (params.keyword) queryParams.append('keyword', params.keyword)
    if (params.category) queryParams.append('category', params.category)
    if (params.is_favorite !== undefined) queryParams.append('is_favorite', params.is_favorite)

    return request.get(`/websites/?${queryParams.toString()}`)
  },

  /**
   * 获取分类列表
   */
  getCategories() {
    return request.get('/websites/categories')
  },

  /**
   * 获取网站详情
   * @param {number} id - 网站ID
   */
  getWebsite(id) {
    return request.get(`/websites/${id}`)
  },

  /**
   * 更新网站
   * @param {number} id - 网站ID
   * @param {Object} data - 更新数据
   * @param {string} [data.name] - 网站名称
   * @param {string} [data.url] - 网站URL
   * @param {string} [data.category] - 分类
   * @param {string} [data.description] - 描述
   * @param {boolean} [data.is_favorite] - 是否收藏
   */
  updateWebsite(id, data) {
    const params = new URLSearchParams()

    if (data.name !== undefined) params.append('name', data.name)
    if (data.url !== undefined) params.append('url', data.url)
    if (data.category !== undefined) params.append('category', data.category)
    if (data.description !== undefined) params.append('description', data.description)
    if (data.is_favorite !== undefined) params.append('is_favorite', data.is_favorite)

    return request.put(`/websites/${id}?${params.toString()}`)
  },

  /**
   * 删除网站
   * @param {number} id - 网站ID
   */
  deleteWebsite(id) {
    return request.delete(`/websites/${id}`)
  }
}

export default websitesService
