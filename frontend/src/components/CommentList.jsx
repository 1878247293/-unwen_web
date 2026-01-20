import React, { useState, useEffect } from 'react'
import {
  List,
  Avatar,
  Button,
  Space,
  Modal,
  Input,
  message,
  Pagination,
  Empty,
  Tooltip
} from 'antd'
import {
  MessageOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined
} from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import commentService from '../services/commentService'
import CommentInput from './CommentInput'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const { TextArea } = Input

const CommentItem = ({ comment, onEdit, onDelete, onReply, currentUserId, isAdmin }) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editContent, setEditContent] = useState(comment.content)
  const [isReplying, setIsReplying] = useState(false)

  const canEdit = currentUserId === comment.user_id
  const canDelete = currentUserId === comment.user_id || isAdmin

  const handleSaveEdit = async () => {
    if (!editContent.trim()) {
      message.warning('评论内容不能为空')
      return
    }

    try {
      await onEdit(comment.id, editContent.trim())
      setIsEditing(false)
    } catch (error) {
      // Error handled in parent
    }
  }

  const handleReplyAdded = (newReply) => {
    setIsReplying(false)
    if (onReply) {
      onReply(newReply)
    }
  }

  return (
    <div style={{ marginBottom: '16px' }}>
      <List.Item
        actions={[
          <Button
            type="link"
            size="small"
            icon={<MessageOutlined />}
            onClick={() => setIsReplying(!isReplying)}
          >
            回复
          </Button>,
          canEdit && (
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => {
                setIsEditing(true)
                setEditContent(comment.content)
              }}
            >
              编辑
            </Button>
          ),
          canDelete && (
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={() => onDelete(comment.id)}
            >
              删除
            </Button>
          )
        ].filter(Boolean)}
      >
        <List.Item.Meta
          avatar={
            comment.user?.avatar ? (
              <Avatar src={comment.user.avatar} />
            ) : (
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
            )
          }
          title={
            <Space>
              <span style={{ fontWeight: 'bold' }}>{comment.user?.username || '未知用户'}</span>
              <Tooltip title={dayjs(comment.created_at).format('YYYY-MM-DD HH:mm:ss')}>
                <span style={{ fontSize: '12px', color: '#999' }}>
                  {dayjs(comment.created_at).fromNow()}
                </span>
              </Tooltip>
              {comment.created_at !== comment.updated_at && (
                <span style={{ fontSize: '12px', color: '#999' }}>(已编辑)</span>
              )}
            </Space>
          }
          description={
            isEditing ? (
              <div style={{ marginTop: '8px' }}>
                <TextArea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  autoSize={{ minRows: 2, maxRows: 6 }}
                  maxLength={5000}
                />
                <div style={{ marginTop: '8px' }}>
                  <Space>
                    <Button size="small" type="primary" onClick={handleSaveEdit}>
                      保存
                    </Button>
                    <Button size="small" onClick={() => setIsEditing(false)}>
                      取消
                    </Button>
                  </Space>
                </div>
              </div>
            ) : (
              <div style={{ marginTop: '8px', whiteSpace: 'pre-wrap' }}>{comment.content}</div>
            )
          }
        />
      </List.Item>

      {/* 回复输入框 */}
      {isReplying && (
        <div style={{ marginLeft: '48px', marginTop: '8px', marginBottom: '16px' }}>
          <CommentInput
            paperId={comment.paper_id}
            parentId={comment.id}
            onCommentAdded={handleReplyAdded}
            placeholder={`回复 @${comment.user?.username}...`}
          />
        </div>
      )}

      {/* 回复列表 */}
      {comment.replies && comment.replies.length > 0 && (
        <div style={{ marginLeft: '48px', marginTop: '16px' }}>
          {comment.replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              onEdit={onEdit}
              onDelete={onDelete}
              onReply={onReply}
              currentUserId={currentUserId}
              isAdmin={isAdmin}
            />
          ))}
        </div>
      )}
    </div>
  )
}

const CommentList = ({ paperId }) => {
  const { user } = useAuthStore()
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [sortOrder, setSortOrder] = useState('desc')

  // 加载评论列表
  const loadComments = async () => {
    setLoading(true)
    try {
      const response = await commentService.getPaperComments(paperId, {
        page,
        page_size: pageSize,
        sort_order: sortOrder
      })

      if (response.code === 200) {
        setComments(response.data.comments || [])
        setTotal(response.data.total || 0)
      } else {
        message.error(response.message || '加载评论失败')
      }
    } catch (error) {
      message.error('加载评论失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadComments()
  }, [paperId, page, pageSize, sortOrder])

  // 处理新评论添加
  const handleCommentAdded = (newComment) => {
    // 刷新评论列表
    loadComments()
  }

  // 处理编辑评论
  const handleEdit = async (commentId, content) => {
    try {
      const response = await commentService.updateComment(commentId, { content })

      if (response.code === 200) {
        message.success('评论更新成功')
        loadComments()
      } else {
        message.error(response.message || '更新失败')
      }
    } catch (error) {
      message.error('更新失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  // 处理删除评论
  const handleDelete = (commentId) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这条评论吗？此操作不可恢复。',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await commentService.deleteComment(commentId)

          if (response.code === 200) {
            message.success('评论删除成功')
            loadComments()
          } else {
            message.error(response.message || '删除失败')
          }
        } catch (error) {
          message.error('删除失败: ' + (error.response?.data?.detail || error.message))
        }
      }
    })
  }

  // 处理回复
  const handleReply = (newReply) => {
    // 刷新评论列表以显示新回复
    loadComments()
  }

  // 处理分页改变
  const handlePageChange = (newPage, newPageSize) => {
    setPage(newPage)
    setPageSize(newPageSize)
  }

  return (
    <div>
      {/* 评论输入框 */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{ marginBottom: '16px' }}>
          评论 ({total})
          <Button
            type="link"
            size="small"
            onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
            style={{ marginLeft: '8px' }}
          >
            {sortOrder === 'desc' ? '最新在前' : '最早在前'}
          </Button>
        </h3>
        <CommentInput paperId={paperId} onCommentAdded={handleCommentAdded} />
      </div>

      {/* 评论列表 */}
      <List
        loading={loading}
        dataSource={comments}
        locale={{
          emptyText: <Empty description="暂无评论，快来发表第一条评论吧！" />
        }}
        renderItem={(comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onReply={handleReply}
            currentUserId={user?.id}
            isAdmin={user?.role === 'admin'}
          />
        )}
      />

      {/* 分页 */}
      {total > pageSize && (
        <div style={{ marginTop: '16px', textAlign: 'center' }}>
          <Pagination
            current={page}
            pageSize={pageSize}
            total={total}
            onChange={handlePageChange}
            showSizeChanger
            showQuickJumper
            showTotal={(total) => `共 ${total} 条评论`}
            pageSizeOptions={['10', '20', '50']}
          />
        </div>
      )}
    </div>
  )
}

export default CommentList
