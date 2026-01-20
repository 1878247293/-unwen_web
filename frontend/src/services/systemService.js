/**
 * 系统监控相关API服务
 */
import request from './request'

const systemService = {
  /**
   * 获取系统资源使用情况
   * @returns {Promise} CPU、内存、磁盘使用率
   */
  getResources: async () => {
    return request.get('/system/resources')
  },

  /**
   * 获取系统统计信息
   * @returns {Promise} 用户数、论文数、讨论数等统计数据
   */
  getStatistics: async () => {
    return request.get('/system/statistics')
  },

  /**
   * 获取存储使用情况
   * @returns {Promise} 上传文件大小、数据库大小
   */
  getStorage: async () => {
    return request.get('/system/storage')
  },

  /**
   * 获取系统健康状态
   * @returns {Promise} 系统健康检查结果
   */
  getHealth: async () => {
    return request.get('/system/health')
  }
}

export default systemService
