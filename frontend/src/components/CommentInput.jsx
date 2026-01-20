import React, { useState } from 'react'
import { Input, Button, message } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import commentService from '../services/commentService'

const { TextArea } = Input

const CommentInput = ({ paperId, parentId = null, onCommentAdded, placeholder = '发表评论...' }) => {
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!content.trim()) {
      message.warning('评论内容不能为空')
      return
    }

    setSubmitting(true)
    try {
      const response = await commentService.createComment(paperId, {
        content: content.trim(),
        parent_id: parentId
      })

      if (response.code === 200) {
        message.success(parentId ? '回复成功' : '评论成功')
        setContent('')
        if (onCommentAdded) {
          onCommentAdded(response.data)
        }
      } else {
        message.error(response.message || '评论失败')
      }
    } catch (error) {
      message.error('评论失败: ' + (error.response?.data?.detail || error.message))
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
      <div style={{ marginTop: '8px', textAlign: 'right' }}>
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSubmit}
          loading={submitting}
          disabled={!content.trim()}
        >
          {parentId ? '回复' : '发表评论'}
        </Button>
      </div>
    </div>
  )
}

export default CommentInput
