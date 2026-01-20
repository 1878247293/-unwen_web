import React, { useState, useEffect } from 'react'
import { Tour } from 'antd'
import { useLocation } from 'react-router-dom'
import './UserTour.css'

/**
 * 用户引导Tour组件
 * 为新用户提供功能引导
 */

// Dashboard页面引导步骤
const dashboardSteps = [
  {
    title: '欢迎使用科研论文管理系统 🎉',
    description: '让我们快速了解一下系统的主要功能吧！',
    target: null, // 居中显示
  },
  {
    title: '统计数据',
    description: '这里显示您的论文、笔记和标签的统计信息，帮助您快速了解研究进度。',
    target: () => document.querySelector('.dashboard-stats'),
  },
  {
    title: '阅读进度',
    description: '查看您的阅读进度，包括未读、在读和已读论文的分布情况。',
    target: () => document.querySelector('.reading-progress-section'),
  },
  {
    title: '最近阅读',
    description: '快速访问您最近阅读的论文，继续之前的研究工作。',
    target: () => document.querySelector('.recent-papers-section'),
  },
]

// 论文列表页面引导步骤
const papersSteps = [
  {
    title: '论文管理',
    description: '这是您的论文库，可以在这里管理所有研究论文。',
    target: null,
  },
  {
    title: '搜索功能',
    description: '使用搜索框快速查找论文，支持标题、作者、关键词搜索。快捷键：Ctrl+K',
    target: () => document.querySelector('.papers-search-bar'),
  },
  {
    title: '添加论文',
    description: '点击这里添加新论文，支持上传PDF和手动输入信息。快捷键：Ctrl+N',
    target: () => document.querySelector('.add-paper-btn'),
  },
  {
    title: '筛选和排序',
    description: '使用这些工具按年份、状态、标签等筛选和排序论文。',
    target: () => document.querySelector('.papers-filters'),
  },
  {
    title: '操作按钮',
    description: '每篇论文都有查看、编辑、删除等操作，点击即可使用。',
    target: () => document.querySelector('.ant-table-tbody tr:first-child .ant-space'),
  },
]

// 论文详情页面引导步骤
const paperDetailSteps = [
  {
    title: '论文详情',
    description: '查看论文的完整信息，包括摘要、作者、发表信息等。',
    target: null,
  },
  {
    title: '阅读进度',
    description: '使用滑块记录您的阅读进度，系统会自动更新阅读状态。',
    target: () => document.querySelector('.reading-progress-slider'),
  },
  {
    title: '标签管理',
    description: '为论文添加标签，方便分类和查找。',
    target: () => document.querySelector('.paper-tags-section'),
  },
  {
    title: '笔记功能',
    description: '切换到笔记标签页，为论文添加研究笔记和想法。支持Markdown格式。',
    target: () => document.querySelector('.ant-tabs-tab:nth-child(2)'),
  },
]

// 标签管理页面引导步骤
const tagsSteps = [
  {
    title: '标签管理',
    description: '创建和管理标签，帮助您组织和分类论文。',
    target: null,
  },
  {
    title: '创建标签',
    description: '点击这里创建新标签，可以自定义标签名称和颜色。',
    target: () => document.querySelector('.create-tag-btn'),
  },
  {
    title: '标签列表',
    description: '查看所有标签及其关联的论文数量，点击可以筛选相关论文。',
    target: () => document.querySelector('.ant-table-wrapper'),
  },
]

export const UserTour = () => {
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [steps, setSteps] = useState([])

  // 检查是否是新用户
  const isNewUser = () => {
    const hasSeenTour = localStorage.getItem('has-seen-tour')
    return !hasSeenTour
  }

  // 根据路径选择引导步骤
  useEffect(() => {
    if (!isNewUser()) return

    let tourSteps = []
    const path = location.pathname

    if (path === '/' || path === '/dashboard') {
      tourSteps = dashboardSteps
    } else if (path === '/papers') {
      tourSteps = papersSteps
    } else if (path.startsWith('/papers/') && path.includes('/detail')) {
      tourSteps = paperDetailSteps
    } else if (path === '/tags') {
      tourSteps = tagsSteps
    }

    if (tourSteps.length > 0) {
      setSteps(tourSteps)
      // 延迟显示，等待DOM渲染完成
      setTimeout(() => setOpen(true), 500)
    }
  }, [location.pathname])

  const handleClose = () => {
    setOpen(false)
    // 标记用户已看过引导
    localStorage.setItem('has-seen-tour', 'true')
  }

  if (steps.length === 0) return null

  return (
    <Tour
      open={open}
      onClose={handleClose}
      steps={steps}
      indicatorsRender={(current, total) => (
        <span className="tour-indicators">
          {current + 1} / {total}
        </span>
      )}
    />
  )
}

/**
 * 手动触发引导
 */
export const TriggerTourButton = () => {
  const [open, setOpen] = useState(false)
  const location = useLocation()

  const handleStartTour = () => {
    // 临时移除已看过标记
    localStorage.removeItem('has-seen-tour')
    // 刷新页面以重新触发引导
    window.location.reload()
  }

  return (
    <button
      className="trigger-tour-btn"
      onClick={handleStartTour}
      title="重新查看新手引导"
    >
      <span className="tour-icon">?</span>
    </button>
  )
}

/**
 * 重置引导状态的工具函数
 */
export const resetTourStatus = () => {
  localStorage.removeItem('has-seen-tour')
}

export default UserTour
