import { useEffect } from 'react'

/**
 * 预加载路由Hook
 * 在空闲时间预加载懒加载的组件
 */
function usePreloadRoutes() {
  useEffect(() => {
    // 在浏览器空闲时预加载常用页面
    if ('requestIdleCallback' in window) {
      const preloadComponents = () => {
        // 预加载标签管理（高频访问）
        requestIdleCallback(() => {
          import('../pages/Tags')
        })

        // 预加载通知页面（高频访问）
        requestIdleCallback(() => {
          import('../pages/Notifications')
        })

        // 预加载个人中心（中频访问）
        requestIdleCallback(() => {
          import('../pages/Profile')
        })

        // 预加载想法收集（中频访问）
        requestIdleCallback(() => {
          import('../pages/Ideas')
        })

        // 预加载改进建议（中频访问）
        requestIdleCallback(() => {
          import('../pages/Suggestions')
        })

        // 预加载添加论文（中频访问）
        requestIdleCallback(() => {
          import('../pages/AddPaper')
        })
      }

      // 延迟2秒后开始预加载，避免影响首屏
      const timer = setTimeout(preloadComponents, 2000)

      return () => clearTimeout(timer)
    }
  }, [])
}

export default usePreloadRoutes
