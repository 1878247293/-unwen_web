/**
 * 标签相关的API服务
 */

import request from './request'
import { cachedGet, clearCache } from './cachedRequest'

const tagService = {
  /**
   * 创建标签
   * @param {Object} tagData - 标签数据 {name, color}
   * @returns {Promise}
   */
  createTag: async (tagData) => {
    const response = await request.post('/tags/', tagData)
    // 创建标签后清除标签列表缓存
    clearCache('/tags/')
    return response
  },

  /**
   * 获取标签列表（使用缓存，5分钟）
   * @returns {Promise}
   */
  getTags: async () => {
    return cachedGet('/tags/', {}, 5 * 60 * 1000) // 缓存5分钟
  },

  /**
   * 获取标签详情（使用缓存，3分钟）
   * @param {number} tagId - 标签ID
   * @returns {Promise}
   */
  getTag: async (tagId) => {
    return cachedGet(`/tags/${tagId}`, {}, 3 * 60 * 1000) // 缓存3分钟
  },

  /**
   * 更新标签
   * @param {number} tagId - 标签ID
   * @param {Object} tagData - 标签数据
   * @returns {Promise}
   */
  updateTag: async (tagId, tagData) => {
    const response = await request.put(`/tags/${tagId}`, tagData)
    // 更新标签后清除相关缓存
    clearCache('/tags/')
    clearCache(`/tags/${tagId}`)
    return response
  },

  /**
   * 删除标签
   * @param {number} tagId - 标签ID
   * @returns {Promise}
   */
  deleteTag: async (tagId) => {
    const response = await request.delete(`/tags/${tagId}`)
    // 删除标签后清除相关缓存
    clearCache('/tags/')
    clearCache(`/tags/${tagId}`)
    return response
  },

  /**
   * 为论文添加标签
   * @param {number} paperId - 论文ID
   * @param {Array} tagIds - 标签ID数组
   * @returns {Promise}
   */
  addTagsToPaper: async (paperId, tagIds) => {
    const response = await request.post(`/tags/papers/${paperId}/tags`, { tag_ids: tagIds })
    // 添加标签后清除论文标签缓存
    clearCache(`/tags/papers/${paperId}/tags`)
    return response
  },

  /**
   * 从论文移除标签
   * @param {number} paperId - 论文ID
   * @param {number} tagId - 标签ID
   * @returns {Promise}
   */
  removeTagFromPaper: async (paperId, tagId) => {
    const response = await request.delete(`/tags/papers/${paperId}/tags/${tagId}`)
    // 移除标签后清除论文标签缓存
    clearCache(`/tags/papers/${paperId}/tags`)
    return response
  },

  /**
   * 获取论文的所有标签（使用缓存，3分钟）
   * @param {number} paperId - 论文ID
   * @returns {Promise}
   */
  getPaperTags: async (paperId) => {
    return cachedGet(`/tags/papers/${paperId}/tags`, {}, 3 * 60 * 1000) // 缓存3分钟
  }
}

export default tagService
