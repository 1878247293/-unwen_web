import request from './request'
import cache from '../utils/cache'

/**
 * 带缓存的GET请求
 * @param {string} url - 请求URL
 * @param {object} config - axios配置
 * @param {number} cacheTTL - 缓存过期时间（毫秒），默认5分钟
 * @returns {Promise} - 响应数据
 */
export const cachedGet = async (url, config = {}, cacheTTL = 5 * 60 * 1000) => {
  const cacheKey = cache.generateKey(url, config.params)

  // 尝试从缓存获取
  const cachedData = cache.get(cacheKey)
  if (cachedData) {
    console.log('✅ [Cache] 命中缓存:', url)
    return Promise.resolve(cachedData)
  }

  console.log('🔄 [Cache] 未命中，发起请求:', url)

  try {
    // 发起实际请求
    const response = await request.get(url, config)

    // 只缓存成功的响应
    if (response && response.code === 200) {
      cache.set(cacheKey, response, cacheTTL)
      console.log('💾 [Cache] 已缓存:', url)
    }

    return response
  } catch (error) {
    // 请求失败时不缓存
    throw error
  }
}

/**
 * 清除指定URL的缓存
 * @param {string} url - 请求URL
 * @param {object} params - 请求参数
 */
export const clearCache = (url, params = {}) => {
  const cacheKey = cache.generateKey(url, params)
  cache.delete(cacheKey)
  console.log('🗑️ [Cache] 已清除缓存:', url)
}

/**
 * 清除所有缓存
 */
export const clearAllCache = () => {
  cache.clear()
  console.log('🗑️ [Cache] 已清除所有缓存')
}

// 导出原始request，用于POST/PUT/DELETE等不需要缓存的请求
export { request as default }
