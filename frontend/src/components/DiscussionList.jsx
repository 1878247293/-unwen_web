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
  Tooltip,
  Tag
} from 'antd'
import {
  MessageOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  HeartOutlined,
  HeartFilled,
  StarOutlined,
  StarFilled,
  WarningOutlined,
  EyeInvisibleOutlined,
  EyeOutlined
} from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import discussionService from '../services/discussionService'
import DiscussionInput from './DiscussionInput'
import ReportModal from './ReportModal'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const { TextArea } = Input

const DiscussionItem = ({
  discussion,
  onEdit,
  onDelete,
  onReply,
  onLike,
  onFavorite,
  onHide,
  onUnhide,
  onReportClick,
  currentUserId,
  isAdmin
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editContent, setEditContent] = useState(discussion.content)
  const [isReplying, setIsReplying] = useState(false)

  const canEdit = currentUserId === discussion.user_id
  const canDelete = currentUserId === discussion.user_id || isAdmin

  const handleSaveEdit = async () => {
    if (!editContent.trim()) {
      message.warning('讨论内容不能为空')
      return
    }

    try {
      await onEdit(discussion.id, editContent.trim())
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

  const displayName = discussion.is_anonymous ? '匿名用户' : (discussion.user?.username || '未知用户')
  const isLiked = discussion.user_liked || false
  const isFavorited = discussion.user_favorited || false

  return (
    <div style={{ marginBottom: '16px' }}>
      <List.Item
        actions={[
          <Tooltip title={isLiked ? '取消点赞' : '点赞'}>
            <Button
              type="link"
              size="small"
              icon={isLiked ? <HeartFilled style={{ color: '#ff4d4f' }} /> : <HeartOutlined />}
              onClick={() => onLike(discussion.id, isLiked)}
            >
              {discussion.likes_count || 0}
            </Button>
          </Tooltip>,
          <Tooltip title={isFavorited ? '取消收藏' : '收藏'}>
            <Button
              type="link"
              size="small"
              icon={isFavorited ? <StarFilled style={{ color: '#faad14' }} /> : <StarOutlined />}
              onClick={() => onFavorite(discussion.id, isFavorited)}
            >
              收藏
            </Button>
          </Tooltip>,
          <Button
            type="link"
            size="small"
            icon={<MessageOutlined />}
            onClick={() => setIsReplying(!isReplying)}
          >
            回复
          </Button>,
          !discussion.is_anonymous && canEdit && (
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => {
                setIsEditing(true)
                setEditContent(discussion.content)
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
              onClick={() => onDelete(discussion.id)}
            >
              删除
            </Button>
          ),
          !canEdit && (
            <Button
              type="link"
              size="small"
              icon={<WarningOutlined />}
              onClick={() => onReportClick(discussion.id)}
            >
              举报
            </Button>
          ),
          isAdmin && !discussion.is_hidden && (
            <Button
              type="link"
              size="small"
              icon={<EyeInvisibleOutlined />}
              onClick={() => onHide(discussion.id)}
            >
              隐藏
            </Button>
          ),
          isAdmin && discussion.is_hidden && (
            <Button
              type="link"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => onUnhide(discussion.id)}
            >
              取消隐藏
            </Button>
          )
        ].filter(Boolean)}
      >
        <List.Item.Meta
          avatar={
            discussion.is_anonymous ? (
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#999' }} />
            ) : discussion.user?.avatar ? (
              <Avatar src={discussion.user.avatar} />
            ) : (
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
            )
          }
          title={
            <Space>
              <span style={{ fontWeight: 'bold' }}>{displayName}</span>
              <Tooltip title={dayjs(discussion.created_at).format('YYYY-MM-DD HH:mm:ss')}>
                <span style={{ fontSize: '12px', color: '#999' }}>
                  {dayjs(discussion.created_at).fromNow()}
                </span>
              </Tooltip>
              {discussion.created_at !== discussion.updated_at && (
                <span style={{ fontSize: '12px', color: '#999' }}>(已编辑)</span>
              )}
              {discussion.is_anonymous && (
                <Tag color="default">匿名</Tag>
              )}
              {discussion.is_hidden && (
                <Tag color="red">已隐藏</Tag>
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
                  showCount
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
              <div style={{ marginTop: '8px', whiteSpace: 'pre-wrap' }}>{discussion.content}</div>
            )
          }
        />
      </List.Item>

      {/* 回复输入框 */}
      {isReplying && (
        <div style={{ marginLeft: '48px', marginTop: '8px', marginBottom: '16px' }}>
          <DiscussionInput
            parentId={discussion.id}
            onDiscussionAdded={handleReplyAdded}
            placeholder={`回复 @${displayName}...`}
            showAnonymousOption={true}
          />
        </div>
      )}

      {/* 回复列表 */}
      {discussion.replies && discussion.replies.length > 0 && (
        <div style={{ marginLeft: '48px', marginTop: '16px' }}>
          {discussion.replies.map((reply) => (
            <DiscussionItem
              key={reply.id}
              discussion={reply}
              onEdit={onEdit}
              onDelete={onDelete}
              onReply={onReply}
              onLike={onLike}
              onFavorite={onFavorite}
              onHide={onHide}
              onUnhide={onUnhide}
              onReportClick={onReportClick}
              currentUserId={currentUserId}
              isAdmin={isAdmin}
            />
          ))}
        </div>
      )}
    </div>
  )
}

const DiscussionList = ({ showHidden = false }) => {
  const { user } = useAuthStore()
  const [discussions, setDiscussions] = useState([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [sortOrder, setSortOrder] = useState('newest')
  const [reportModalVisible, setReportModalVisible] = useState(false)
  const [reportingDiscussionId, setReportingDiscussionId] = useState(null)

  const isAdmin = user?.role === 'admin'

  // 加载讨论列表
  const loadDiscussions = async () => {
    setLoading(true)
    try {
      const response = await discussionService.getDiscussions({
        page,
        page_size: pageSize,
        sort_order: sortOrder,
        show_hidden: showHidden
      })

      if (response.code === 200) {
        setDiscussions(response.data.discussions || [])
        setTotal(response.data.total || 0)
      } else {
        message.error(response.message || '加载讨论失败')
      }
    } catch (error) {
      message.error('加载讨论失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDiscussions()
  }, [page, pageSize, sortOrder, showHidden])

  // 处理新讨论添加
  const handleDiscussionAdded = (newDiscussion) => {
    // 刷新讨论列表
    loadDiscussions()
  }

  // 处理编辑讨论
  const handleEdit = async (discussionId, content) => {
    try {
      const response = await discussionService.updateDiscussion(discussionId, { content })

      if (response.code === 200) {
        message.success('讨论更新成功')
        loadDiscussions()
      } else {
        message.error(response.message || '更新失败')
      }
    } catch (error) {
      message.error('更新失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  // 处理删除讨论
  const handleDelete = (discussionId) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这条讨论吗？此操作不可恢复。',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await discussionService.deleteDiscussion(discussionId)

          if (response.code === 200) {
            message.success('讨论删除成功')
            loadDiscussions()
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
    // 刷新讨论列表以显示新回复
    loadDiscussions()
  }

  // 处理点赞（乐观更新）
  const handleLike = async (discussionId, isLiked) => {
    // 乐观更新：先更新本地状态
    const updateDiscussionLikes = (discussions) => {
      return discussions.map(discussion => {
        if (discussion.id === discussionId) {
          return {
            ...discussion,
            user_liked: !isLiked,
            likes_count: isLiked ? (discussion.likes_count || 1) - 1 : (discussion.likes_count || 0) + 1
          }
        }
        // 递归更新回复
        if (discussion.replies && discussion.replies.length > 0) {
          return {
            ...discussion,
            replies: updateDiscussionLikes(discussion.replies)
          }
        }
        return discussion
      })
    }

    // 立即更新本地状态，不等待API响应
    setDiscussions(prev => updateDiscussionLikes(prev))

    try {
      const response = isLiked
        ? await discussionService.unlikeDiscussion(discussionId)
        : await discussionService.likeDiscussion(discussionId)

      if (response.code === 200) {
        // 操作成功，无需提示（已经更新了UI）
      } else {
        // 操作失败，回滚状态
        message.error(response.message || '操作失败')
        setDiscussions(prev => updateDiscussionLikes(prev)) // 回滚
      }
    } catch (error) {
      // 操作失败，回滚状态
      message.error('操作失败: ' + (error.response?.data?.detail || error.message))
      setDiscussions(prev => updateDiscussionLikes(prev)) // 回滚
    }
  }

  // 处理收藏（乐观更新）
  const handleFavorite = async (discussionId, isFavorited) => {
    // 乐观更新：先更新本地状态
    const updateDiscussionFavorites = (discussions) => {
      return discussions.map(discussion => {
        if (discussion.id === discussionId) {
          return {
            ...discussion,
            user_favorited: !isFavorited
          }
        }
        // 递归更新回复
        if (discussion.replies && discussion.replies.length > 0) {
          return {
            ...discussion,
            replies: updateDiscussionFavorites(discussion.replies)
          }
        }
        return discussion
      })
    }

    // 立即更新本地状态
    setDiscussions(prev => updateDiscussionFavorites(prev))

    try {
      const response = isFavorited
        ? await discussionService.unfavoriteDiscussion(discussionId)
        : await discussionService.favoriteDiscussion(discussionId)

      if (response.code === 200) {
        // 操作成功，无需提示（已经更新了UI）
      } else {
        // 操作失败，回滚状态
        message.error(response.message || '操作失败')
        setDiscussions(prev => updateDiscussionFavorites(prev)) // 回滚
      }
    } catch (error) {
      // 操作失败，回滚状态
      message.error('操作失败: ' + (error.response?.data?.detail || error.message))
      setDiscussions(prev => updateDiscussionFavorites(prev)) // 回滚
    }
  }

  // 处理隐藏（乐观更新）
  const handleHide = async (discussionId) => {
    // 乐观更新：先更新本地状态
    const updateDiscussionHidden = (discussions) => {
      return discussions.map(discussion => {
        if (discussion.id === discussionId) {
          return {
            ...discussion,
            is_hidden: true
          }
        }
        if (discussion.replies && discussion.replies.length > 0) {
          return {
            ...discussion,
            replies: updateDiscussionHidden(discussion.replies)
          }
        }
        return discussion
      })
    }

    setDiscussions(prev => updateDiscussionHidden(prev))

    try {
      const response = await discussionService.hideDiscussion(discussionId)

      if (response.code === 200) {
        message.success('已隐藏讨论')
      } else {
        message.error(response.message || '操作失败')
        // 回滚
        setDiscussions(prev => updateDiscussionHidden(prev))
      }
    } catch (error) {
      message.error('操作失败: ' + (error.response?.data?.detail || error.message))
      setDiscussions(prev => updateDiscussionHidden(prev))
    }
  }

  // 处理取消隐藏（乐观更新）
  const handleUnhide = async (discussionId) => {
    // 乐观更新：先更新本地状态
    const updateDiscussionUnhidden = (discussions) => {
      return discussions.map(discussion => {
        if (discussion.id === discussionId) {
          return {
            ...discussion,
            is_hidden: false
          }
        }
        if (discussion.replies && discussion.replies.length > 0) {
          return {
            ...discussion,
            replies: updateDiscussionUnhidden(discussion.replies)
          }
        }
        return discussion
      })
    }

    setDiscussions(prev => updateDiscussionUnhidden(prev))

    try {
      const response = await discussionService.unhideDiscussion(discussionId)

      if (response.code === 200) {
        message.success('已取消隐藏')
      } else {
        message.error(response.message || '操作失败')
        // 回滚
        setDiscussions(prev => updateDiscussionUnhidden(prev))
      }
    } catch (error) {
      message.error('操作失败: ' + (error.response?.data?.detail || error.message))
      setDiscussions(prev => updateDiscussionUnhidden(prev))
    }
  }

  // 处理举报点击
  const handleReportClick = (discussionId) => {
    setReportingDiscussionId(discussionId)
    setReportModalVisible(true)
  }

  // 处理举报提交
  const handleReportSubmitted = () => {
    // 不需要刷新列表，举报不影响显示
  }

  // 处理分页改变
  const handlePageChange = (newPage, newPageSize) => {
    setPage(newPage)
    setPageSize(newPageSize)
  }

  // 切换排序
  const handleSortChange = () => {
    const sortOptions = ['newest', 'oldest', 'hottest']
    const currentIndex = sortOptions.indexOf(sortOrder)
    const nextIndex = (currentIndex + 1) % sortOptions.length
    setSortOrder(sortOptions[nextIndex])
    setPage(1)
  }

  const getSortLabel = () => {
    switch (sortOrder) {
      case 'newest':
        return '最新在前'
      case 'oldest':
        return '最早在前'
      case 'hottest':
        return '最热在前'
      default:
        return '最新在前'
    }
  }

  return (
    <div>
      {/* 讨论列表 */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{ marginBottom: '16px' }}>
          讨论 ({total})
          <Button
            type="link"
            size="small"
            onClick={handleSortChange}
            style={{ marginLeft: '8px' }}
          >
            {getSortLabel()}
          </Button>
        </h3>
      </div>

      <List
        loading={loading}
        dataSource={discussions}
        locale={{
          emptyText: <Empty description="暂无讨论，快来发表第一条讨论吧！" />
        }}
        renderItem={(discussion) => (
          <DiscussionItem
            key={discussion.id}
            discussion={discussion}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onReply={handleReply}
            onLike={handleLike}
            onFavorite={handleFavorite}
            onHide={handleHide}
            onUnhide={handleUnhide}
            onReportClick={handleReportClick}
            currentUserId={user?.id}
            isAdmin={isAdmin}
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
            showTotal={(total) => `共 ${total} 条讨论`}
            pageSizeOptions={['10', '20', '50']}
          />
        </div>
      )}

      {/* 举报Modal */}
      <ReportModal
        visible={reportModalVisible}
        onClose={() => setReportModalVisible(false)}
        discussionId={reportingDiscussionId}
        onReportSubmitted={handleReportSubmitted}
      />
    </div>
  )
}

export default DiscussionList
