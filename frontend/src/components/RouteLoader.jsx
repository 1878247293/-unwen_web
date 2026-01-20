import { Suspense } from 'react'
import { Spin } from 'antd'

/**
 * 路由加载包装组件
 * 用于懒加载路由的局部加载状态
 */
function RouteLoader({ children }) {
  return (
    <Suspense
      fallback={
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '400px',
            width: '100%'
          }}
        >
          <Spin size="large" tip="页面加载中..." />
        </div>
      }
    >
      {children}
    </Suspense>
  )
}

export default RouteLoader
