import { useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * 快捷键配置
 */
const SHORTCUTS = {
  SEARCH: { key: 'k', ctrl: true, description: '全局搜索' },
  NEW_PAPER: { key: 'n', ctrl: true, description: '新建论文' },
  DASHBOARD: { key: 'h', ctrl: true, description: '返回首页' },
  PAPERS: { key: 'p', ctrl: true, description: '论文列表' },
  TAGS: { key: 't', ctrl: true, description: '标签管理' },
  HELP: { key: '/', ctrl: false, shift: true, description: '快捷键帮助' },
}

/**
 * 快捷键Hook
 * 用于注册和管理全局快捷键
 */
export const useHotkeys = () => {
  const navigate = useNavigate()

  // 处理快捷键事件
  const handleKeyPress = useCallback((event) => {
    const { key, ctrlKey, metaKey, shiftKey, target } = event

    // 如果焦点在输入框中，忽略某些快捷键
    const isInputFocused = ['INPUT', 'TEXTAREA'].includes(target.tagName)

    // Ctrl+K: 全局搜索
    if ((ctrlKey || metaKey) && key.toLowerCase() === 'k') {
      event.preventDefault()
      // 触发搜索框聚焦
      const searchInput = document.querySelector('.global-search-input')
      if (searchInput) {
        searchInput.focus()
      }
    }

    // Ctrl+N: 新建论文（仅在非输入框时）
    if (!isInputFocused && (ctrlKey || metaKey) && key.toLowerCase() === 'n') {
      event.preventDefault()
      navigate('/papers/add')
    }

    // Ctrl+H: 返回首页
    if ((ctrlKey || metaKey) && key.toLowerCase() === 'h') {
      event.preventDefault()
      navigate('/')
    }

    // Ctrl+P: 论文列表
    if ((ctrlKey || metaKey) && key.toLowerCase() === 'p') {
      event.preventDefault()
      navigate('/papers')
    }

    // Ctrl+T: 标签管理
    if ((ctrlKey || metaKey) && key.toLowerCase() === 't') {
      event.preventDefault()
      navigate('/tags')
    }

    // Shift+/: 快捷键帮助
    if (!isInputFocused && shiftKey && key === '?') {
      event.preventDefault()
      // 触发快捷键帮助模态框
      window.dispatchEvent(new CustomEvent('show-shortcuts-modal'))
    }
  }, [navigate])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress)
    return () => {
      window.removeEventListener('keydown', handleKeyPress)
    }
  }, [handleKeyPress])

  return { SHORTCUTS }
}

/**
 * 快捷键帮助组件
 */
import React, { useState, useEffect } from 'react'
import { Modal, Table, Tag } from 'antd'
import './Shortcuts.css'

export const ShortcutsHelp = () => {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const handleShow = () => setVisible(true)
    window.addEventListener('show-shortcuts-modal', handleShow)
    return () => window.removeEventListener('show-shortcuts-modal', handleShow)
  }, [])

  const columns = [
    {
      title: '快捷键',
      dataIndex: 'shortcut',
      key: 'shortcut',
      width: 150,
      render: (_, record) => {
        const keys = []
        if (record.ctrl) keys.push('Ctrl')
        if (record.shift) keys.push('Shift')
        keys.push(record.key.toUpperCase())

        return (
          <div className="shortcut-keys">
            {keys.map((k, index) => (
              <React.Fragment key={k}>
                {index > 0 && <span className="shortcut-plus">+</span>}
                <Tag color="blue" className="shortcut-key">{k}</Tag>
              </React.Fragment>
            ))}
          </div>
        )
      }
    },
    {
      title: '功能描述',
      dataIndex: 'description',
      key: 'description',
    }
  ]

  const data = Object.entries(SHORTCUTS).map(([id, config]) => ({
    key: id,
    ...config
  }))

  return (
    <Modal
      title="快捷键帮助"
      open={visible}
      onCancel={() => setVisible(false)}
      footer={null}
      width={600}
      className="shortcuts-help-modal"
    >
      <Table
        columns={columns}
        dataSource={data}
        pagination={false}
        size="middle"
      />
      <div className="shortcuts-tip">
        <p>💡 提示：在输入框中时，部分快捷键不可用</p>
        <p>💡 Mac用户：请使用 ⌘ (Command) 代替 Ctrl</p>
      </div>
    </Modal>
  )
}

export default useHotkeys
