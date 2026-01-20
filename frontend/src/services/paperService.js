/**
 * 论文相关的API服务
 */

import request from './request'

const paperService = {
  /**
   * 上传PDF文件
   * @param {File} file - PDF文件
   * @returns {Promise}
   */
  uploadFile: async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    return request.post('/papers/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 创建论文
   * @param {Object} paperData - 论文数据
   * @returns {Promise}
   */
  createPaper: async (paperData) => {
    return request.post('/papers/', paperData)
  },

  /**
   * 获取论文列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getPapers: async (params = {}) => {
    return request.get('/papers/', { params })
  },

  /**
   * 获取论文详情
   * @param {number} paperId - 论文ID
   * @returns {Promise}
   */
  getPaper: async (paperId) => {
    return request.get(`/papers/${paperId}`)
  },

  /**
   * 更新论文
   * @param {number} paperId - 论文ID
   * @param {Object} paperData - 论文数据
   * @returns {Promise}
   */
  updatePaper: async (paperId, paperData) => {
    return request.put(`/papers/${paperId}`, paperData)
  },

  /**
   * 删除论文
   * @param {number} paperId - 论文ID
   * @returns {Promise}
   */
  deletePaper: async (paperId) => {
    return request.delete(`/papers/${paperId}`)
  },

  /**
   * 搜索论文
   * @param {Object} searchParams - 搜索参数
   * @returns {Promise}
   */
  searchPapers: async (searchParams) => {
    return request.get('/papers/', { params: searchParams })
  },

  /**
   * 下载论文PDF
   * @param {number} paperId - 论文ID
   * @param {string} filename - 文件名
   * @returns {Promise}
   */
  downloadPdf: async (paperId, filename) => {
    const token = localStorage.getItem('auth-storage')
    let authToken = ''

    if (token) {
      try {
        const parsed = JSON.parse(token)
        authToken = parsed.state?.token || ''
      } catch (e) {
        console.error('Failed to parse token', e)
      }
    }

    const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/papers/${paperId}/download`

    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '下载失败')
      }

      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = filename || 'paper.pdf'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(downloadUrl)
      document.body.removeChild(a)

      return { success: true }
    } catch (error) {
      throw error
    }
  }
}

export default paperService
