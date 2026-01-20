import React from 'react'
import { Empty, Button } from 'antd'
import { PlusOutlined, SearchOutlined, FileTextOutlined, InboxOutlined } from '@ant-design/icons'
import './EmptyState.css'

const EmptyState = ({
  type = 'default',
  title,
  description,
  actionText,
  onAction
}) => {
  // 预定义的空状态类型
  const emptyTypes = {
    papers: {
      icon: <FileTextOutlined className="empty-icon" />,
      title: '暂无论文',
      description: '您还没有添加任何论文，点击下方按钮开始添加',
      actionText: '添加论文'
    },
    notes: {
      icon: <FileTextOutlined className="empty-icon" />,
      title: '暂无笔记',
      description: '还没有笔记记录，创建第一条笔记吧',
      actionText: '创建笔记'
    },
    search: {
      icon: <SearchOutlined className="empty-icon" />,
      title: '未找到结果',
      description: '没有找到符合条件的内容，试试其他搜索词',
      actionText: '清除筛选'
    },
    tags: {
      icon: <InboxOutlined className="empty-icon" />,
      title: '暂无标签',
      description: '创建标签来更好地组织您的论文',
      actionText: '创建标签'
    },
    default: {
      icon: <InboxOutlined className="empty-icon" />,
      title: '暂无数据',
      description: '这里还没有任何内容',
      actionText: null
    }
  }

  const config = emptyTypes[type] || emptyTypes.default

  return (
    <div className="empty-state-container">
      <div className="empty-state-content">
        {/* SVG插图 */}
        <div className="empty-illustration">
          {config.icon}
          <div className="empty-animation-circle"></div>
          <div className="empty-animation-circle delay-1"></div>
          <div className="empty-animation-circle delay-2"></div>
        </div>

        <h3 className="empty-title">{title || config.title}</h3>
        <p className="empty-description">{description || config.description}</p>

        {(onAction && (actionText || config.actionText)) && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={onAction}
            className="empty-action-button"
          >
            {actionText || config.actionText}
          </Button>
        )}
      </div>
    </div>
  )
}

export default EmptyState
