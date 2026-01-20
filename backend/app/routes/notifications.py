"""
通知管理相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, update
from typing import List, Optional
from datetime import datetime

from app.models import get_db
from app.models.database import User
from app.utils.dependencies import get_current_user
from app.utils.response import success_response, error_response
from sqlalchemy import text

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=dict)
async def get_notifications(
    is_read: Optional[bool] = Query(None, description="筛选已读/未读"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的通知列表

    - 需要登录
    - 只能查看自己的通知
    """
    try:
        # 构建WHERE条件
        where_clause = "WHERE n.user_id = :user_id"
        params = {
            "user_id": current_user.id,
            "limit": page_size,
            "offset": (page - 1) * page_size
        }

        if is_read is not None:
            where_clause += " AND n.is_read = :is_read"
            params["is_read"] = 1 if is_read else 0

        # 查询总数
        count_result = await db.execute(text(f"""
            SELECT COUNT(*) as total
            FROM notifications n
            {where_clause}
        """), params)

        total = count_result.fetchone().total

        # 查询通知列表
        notifications_result = await db.execute(text(f"""
            SELECT
                n.*,
                u.username as sender_username,
                u.avatar as sender_avatar
            FROM notifications n
            LEFT JOIN users u ON n.sender_id = u.id
            {where_clause}
            ORDER BY n.created_at DESC
            LIMIT :limit OFFSET :offset
        """), params)

        notifications = []
        for row in notifications_result.fetchall():
            notifications.append({
                "id": row.id,
                "user_id": row.user_id,
                "type": row.type,
                "title": row.title,
                "content": row.content,
                "link": row.link,
                "is_read": bool(row.is_read),
                "created_at": row.created_at,
                "sender_id": row.sender_id,
                "sender_username": row.sender_username,
                "sender_avatar": row.sender_avatar,
                "related_id": row.related_id
            })

        return success_response(
            data={
                "notifications": notifications,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        return error_response(message=f"获取通知列表失败: {str(e)}")


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取未读通知数量

    - 需要登录
    - 用于显示徽标数字
    """
    try:
        result = await db.execute(text("""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE user_id = :user_id AND is_read = 0
        """), {"user_id": current_user.id})

        count = result.fetchone().count

        return success_response(data={"unread_count": count})
    except Exception as e:
        return error_response(message=f"获取未读通知数量失败: {str(e)}")


@router.put("/{notification_id}/read", response_model=dict)
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记通知为已读

    - 需要登录
    - 只能标记自己的通知
    """
    try:
        # 检查通知是否存在且属于当前用户
        check_result = await db.execute(text("""
            SELECT id, user_id FROM notifications WHERE id = :id
        """), {"id": notification_id})

        notification = check_result.fetchone()
        if not notification:
            return error_response(message="通知不存在", code=404)

        if notification.user_id != current_user.id:
            return error_response(message="无权限操作", code=403)

        # 标记为已读
        await db.execute(text("""
            UPDATE notifications
            SET is_read = 1
            WHERE id = :id
        """), {"id": notification_id})
        await db.commit()

        return success_response(message="已标记为已读")
    except Exception as e:
        await db.rollback()
        return error_response(message=f"操作失败: {str(e)}")


@router.put("/read-all", response_model=dict)
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记所有通知为已读

    - 需要登录
    """
    try:
        await db.execute(text("""
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = :user_id AND is_read = 0
        """), {"user_id": current_user.id})
        await db.commit()

        return success_response(message="所有通知已标记为已读")
    except Exception as e:
        await db.rollback()
        return error_response(message=f"操作失败: {str(e)}")


@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除通知

    - 需要登录
    - 只能删除自己的通知
    """
    try:
        # 检查通知是否存在且属于当前用户
        check_result = await db.execute(text("""
            SELECT id, user_id FROM notifications WHERE id = :id
        """), {"id": notification_id})

        notification = check_result.fetchone()
        if not notification:
            return error_response(message="通知不存在", code=404)

        if notification.user_id != current_user.id:
            return error_response(message="无权限删除", code=403)

        # 删除通知
        await db.execute(text("""
            DELETE FROM notifications WHERE id = :id
        """), {"id": notification_id})
        await db.commit()

        return success_response(message="通知删除成功")
    except Exception as e:
        await db.rollback()
        return error_response(message=f"删除通知失败: {str(e)}")


async def create_notification(
    db: AsyncSession,
    user_id: int,
    type: str,
    title: str,
    content: str,
    link: str = None,
    sender_id: int = None,
    related_id: int = None
):
    """
    创建通知（内部辅助函数）

    通知类型:
    - comment_reply: 评论回复
    - system: 系统通知
    - mention: 提及通知
    """
    try:
        await db.execute(text("""
            INSERT INTO notifications (user_id, type, title, content, link, sender_id, related_id)
            VALUES (:user_id, :type, :title, :content, :link, :sender_id, :related_id)
        """), {
            "user_id": user_id,
            "type": type,
            "title": title,
            "content": content,
            "link": link,
            "sender_id": sender_id,
            "related_id": related_id
        })
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        print(f"创建通知失败: {str(e)}")
        return False
