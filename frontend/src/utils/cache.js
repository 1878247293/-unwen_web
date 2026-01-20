/**
 * 简单的内存缓存工具
 * 用于缓存API响应数据，减少不必要的网络请求
 */

class SimpleCache {
  constructor() {
    this.cache = new Map()
    this.timestamps = new Map()
  }

  /**
   * 生成缓存key
   * @param {string} url - 请求URL
   * @param {object} params - 请求参数
   * @returns {string} - 缓存key
   */
  generateKey(url, params = {}) {
    const sortedParams = Object.keys(params)
      .sort()
      .map(key => `${key}=${JSON.stringify(params[key])}`)
      .join('&')
    return `${url}?${sortedParams}`
  }

  /**
   * 设置缓存
   * @param {string} key - 缓存key
   * @param {*} data - 缓存数据
   * @param {number} ttl - 过期时间（毫秒），默认5分钟
   */
  set(key, data, ttl = 5 * 60 * 1000) {
    this.cache.set(key, data)
    this.timestamps.set(key, Date.now() + ttl)
  }

  /**
   * 获取缓存
   * @param {string} key - 缓存key
   * @returns {*} - 缓存数据，如果不存在或过期则返回null
   */
  get(key) {
    const timestamp = this.timestamps.get(key)

    // 检查是否存在
    if (!this.cache.has(key) || !timestamp) {
      return null
    }

    // 检查是否过期
    if (Date.now() > timestamp) {
      this.delete(key)
      return null
    }

    return this.cache.get(key)
  }

  /**
   * 删除缓存
   * @param {string} key - 缓存key
   */
  delete(key) {
    this.cache.delete(key)
    this.timestamps.delete(key)
  }

  /**
   * 清空所有缓存
   */
  clear() {
    this.cache.clear()
    this.timestamps.clear()
  }

  /**
   * 清理过期缓存
   */
  cleanup() {
    const now = Date.now()
    for (const [key, timestamp] of this.timestamps.entries()) {
      if (now > timestamp) {
        this.delete(key)
      }
    }
  }
}

// 创建单例实例
const cache = new SimpleCache()

// 定期清理过期缓存（每5分钟）
setInterval(() => {
  cache.cleanup()
}, 5 * 60 * 1000)

export default cache
