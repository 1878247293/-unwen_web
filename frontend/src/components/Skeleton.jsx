import React from 'react'
import './Skeleton.css'

/**
 * Skeleton骨架屏组件
 * 用于在内容加载时显示占位符，提升用户体验
 */
const Skeleton = ({
  type = 'text',        // text, title, avatar, image, button, card
  width,                // 自定义宽度
  height,               // 自定义高度
  count = 1,            // 重复次数
  className = '',       // 自定义类名
  animated = true,      // 是否显示动画
  style = {}            // 自定义样式
}) => {
  const getSkeletonClass = () => {
    const baseClass = 'skeleton'
    const classes = [baseClass, `skeleton-${type}`]

    if (animated) {
      classes.push('skeleton-animated')
    }

    if (className) {
      classes.push(className)
    }

    return classes.join(' ')
  }

  const getSkeletonStyle = () => {
    const customStyle = { ...style }

    if (width) {
      customStyle.width = typeof width === 'number' ? `${width}px` : width
    }

    if (height) {
      customStyle.height = typeof height === 'number' ? `${height}px` : height
    }

    return customStyle
  }

  // 渲染单个骨架屏元素
  const renderSkeleton = (index) => (
    <div
      key={index}
      className={getSkeletonClass()}
      style={getSkeletonStyle()}
    />
  )

  // 渲染多个骨架屏元素
  if (count > 1) {
    return (
      <div className="skeleton-group">
        {Array.from({ length: count }).map((_, index) => renderSkeleton(index))}
      </div>
    )
  }

  return renderSkeleton(0)
}

/**
 * 预定义的骨架屏组合组件
 */

// 论文列表项骨架屏
export const PaperListSkeleton = ({ count = 5 }) => (
  <div className="skeleton-paper-list">
    {Array.from({ length: count }).map((_, index) => (
      <div key={index} className="skeleton-paper-item">
        <div className="skeleton-paper-header">
          <Skeleton type="title" width="70%" />
          <div className="skeleton-paper-meta">
            <Skeleton type="text" width={100} />
            <Skeleton type="text" width={80} />
          </div>
        </div>
        <div className="skeleton-paper-body">
          <Skeleton type="text" count={2} />
        </div>
        <div className="skeleton-paper-footer">
          <Skeleton type="button" width={80} />
          <Skeleton type="button" width={80} />
          <Skeleton type="button" width={80} />
        </div>
      </div>
    ))}
  </div>
)

// 论文详情页骨架屏
export const PaperDetailSkeleton = () => (
  <div className="skeleton-paper-detail">
    <Skeleton type="title" width="80%" />
    <div className="skeleton-detail-meta">
      <Skeleton type="text" width={150} />
      <Skeleton type="text" width={120} />
      <Skeleton type="text" width={100} />
    </div>
    <div className="skeleton-detail-content">
      <Skeleton type="text" count={8} />
    </div>
    <div className="skeleton-detail-actions">
      <Skeleton type="button" width={120} />
      <Skeleton type="button" width={120} />
    </div>
  </div>
)

// 卡片骨架屏
export const CardSkeleton = ({ count = 3 }) => (
  <div className="skeleton-card-grid">
    {Array.from({ length: count }).map((_, index) => (
      <div key={index} className="skeleton-card">
        <Skeleton type="image" height={120} />
        <div className="skeleton-card-content">
          <Skeleton type="title" />
          <Skeleton type="text" count={3} />
        </div>
      </div>
    ))}
  </div>
)

// 表格骨架屏
export const TableSkeleton = ({ rows = 5, columns = 4 }) => (
  <div className="skeleton-table">
    <div className="skeleton-table-header">
      {Array.from({ length: columns }).map((_, index) => (
        <Skeleton key={index} type="text" />
      ))}
    </div>
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={rowIndex} className="skeleton-table-row">
        {Array.from({ length: columns }).map((_, colIndex) => (
          <Skeleton key={colIndex} type="text" />
        ))}
      </div>
    ))}
  </div>
)

export default Skeleton
