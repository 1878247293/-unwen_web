/**
 * 笔记相关API服务
 */
import request from './request'

const noteService = {
  /**
   * 为论文创建笔记
   * @param {number} paperId - 论文ID
   * @param {object} noteData - 笔记数据
   * @param {string} noteData.title - 笔记标题（可选）
   * @param {string} noteData.content - 笔记内容（Markdown格式）
   * @param {string} noteData.note_type - 笔记类型（general/summary/method/conclusion/innovation/limitation/thinking）
   * @returns {Promise}
   */
  createNote: async (paperId, noteData) => {
    return request.post(`/notes/papers/${paperId}/notes`, noteData)
  },

  /**
   * 获取论文的所有笔记
   * @param {number} paperId - 论文ID
   * @returns {Promise}
   */
  getPaperNotes: async (paperId) => {
    return request.get(`/notes/papers/${paperId}/notes`)
  },

  /**
   * 获取笔记详情
   * @param {number} noteId - 笔记ID
   * @returns {Promise}
   */
  getNote: async (noteId) => {
    return request.get(`/notes/${noteId}`)
  },

  /**
   * 更新笔记
   * @param {number} noteId - 笔记ID
   * @param {object} noteData - 更新的笔记数据
   * @returns {Promise}
   */
  updateNote: async (noteId, noteData) => {
    return request.put(`/notes/${noteId}`, noteData)
  },

  /**
   * 删除笔记
   * @param {number} noteId - 笔记ID
   * @returns {Promise}
   */
  deleteNote: async (noteId) => {
    return request.delete(`/notes/${noteId}`)
  }
}

export default noteService
