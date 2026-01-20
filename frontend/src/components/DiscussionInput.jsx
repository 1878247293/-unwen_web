import React, { useState, useEffect } from 'react'
import { Input, Button, Checkbox, message } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import discussionService from '../services/discussionService'

const { TextArea } = Input

const DiscussionInput = ({
  parentId = null,
  onDiscussionAdded,
  placeholder = '发表讨论...',
  showAnonymousOption = true
}) => {
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [isAnonymous, setIsAnonymous] = useState(false)
  const [allowAnonymous, setAllowAnonymous] = useState(false)

  // 加载匿名设置
  useEffect(() => {
    const loadAnonymousSetting = async () => {
      if (showAnonymousOption) {
        try {
          const response = await discussionService.getAnonymousSetting()
          if (response.code === 200) {
            setAllowAnonymous(response.data.allow_anonymous)
          }
        } catch (error) {
          // 如果获取失败，默认不允许匿名
          setAllowAnonymous(false)
        }
      }
    }
    loadAnonymousSetting()
  }, [showAnonymousOption])

  const handleSubmit = async () => {
    if (!content.trim()) {
      message.warning('讨论内容不能为空')
      return
    }

    setSubmitting(true)
    try {
      const response = await discussionService.createDiscussion({
        content: content.trim(),
        is_anonymous: isAnonymous,
        parent_id: parentId
      })

      if (response.code === 200) {
        message.success(parentId ? '回复成功' : '发布成功')
        setContent('')
        setIsAnonymous(false)
        if (onDiscussionAdded) {
          onDiscussionAdded(response.data)
        }
      } else {
        message.error(response.message || '发布失败')
      }
    } catch (error) {
      message.error('发布失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSubmitting(false)
    }
  }

  const handleKeyPress = (e) => {
    // Ctrl + Enter 提交
    if (e.ctrlKey && e.key === 'Enter') {
      handleSubmit()
    }
  }

  return (
    <div style={{ marginBottom: '16px' }}>
      <TextArea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        autoSize={{ minRows: 3, maxRows: 6 }}
        maxLength={5000}
        showCount
        disabled={submitting}
      />
      <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          {showAnonymousOption && allowAnonymous && (
            <Checkbox
              checked={isAnonymous}
              onChange={(e) => setIsAnonymous(e.target.checked)}
              disabled={submitting}
            >
              匿名发布
            </Checkbox>
          )}
        </div>
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSubmit}
          loading={submitting}
          disabled={!content.trim()}
        >
          {parentId ? '回复' : '发布'}
        </Button>
      </div>
    </div>
  )
}

export default DiscussionInput
