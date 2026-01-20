"""
改进建议管理相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, update
from typing import List, Optional
from datetime import datetime

from app.models import get_db
from app.models.database import User
from app.utils.dependencies import get_current_user, check_permission
from app.utils.response import success_response, error_response
from sqlalchemy import text

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.post("/", response_model=dict)
async def create_suggestion(
    content: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建改进建议

    - 需要登录
    - 所有用户都可以创建
    """
    try:
        # 创建建议
        result = await db.execute(text("""
            INSERT INTO suggestions (content, user_id, status)
            VALUES (:content, :user_id, 'pending')
        """), {
            "content": content,
            "user_id": current_user.id
        })
        await db.commit()

        suggestion_id = result.lastrowid

        # 获取创建的建议
        suggestion_result = await db.execute(text("""
            SELECT s.*, u.username, u.avatar
            FROM suggestions s
            JOIN users u ON s.user_id = u.id
            WHERE s.id = :id
        """), {"id": suggestion_id})

        suggestion = suggestion_result.fetchone()

        return success_response(
            data={
                "id": suggestion.id,
                "content": suggestion.content,
                "user_id": suggestion.user_id,
                "username": suggestion.username,
                "avatar": suggestion.avatar,
                "status": suggestion.status,
                "created_at": suggestion.created_at,
                "completed_at": suggestion.completed_at,
                "completed_by": suggestion.completed_by
            },
            message="建议创建成功"
        )
    except Exception as e:
        await db.rollback()
        return error_response(message=f"创建建议失败: {str(e)}")


@router.get("/", response_model=dict)
async def get_suggestions(
    status: Optional[str] = Query(None, description="筛选状态: pending, completed"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=1000, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取建议列表

    - 需要登录
    - 所有用户都可以查看所有建议
    """
    try:
        # 构建WHERE条件
        where_clause = "WHERE 1=1"
        params = {
            "limit": page_size,
            "offset": (page - 1) * page_size
        }

        if status:
            where_clause += " AND s.status = :status"
            params["status"] = status

        # 查询总数
        count_result = await db.execute(text(f"""
            SELECT COUNT(*) as total
            FROM suggestions s
            {where_clause}
        """), params)

        total = count_result.fetchone().total

        # 查询建议列表
        suggestions_result = await db.execute(text(f"""
            SELECT
                s.*,
                u.username,
                u.avatar,
                cu.username as completed_by_username
            FROM suggestions s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN users cu ON s.completed_by = cu.id
            {where_clause}
            ORDER BY s.created_at DESC
            LIMIT :limit OFFSET :offset
        """), params)

        suggestions = []
        for row in suggestions_result.fetchall():
            suggestions.append({
                "id": row.id,
                "content": row.content,
                "user_id": row.user_id,
                "username": row.username,
                "avatar": row.avatar,
                "status": row.status,
                "created_at": row.created_at,
                "completed_at": row.completed_at,
                "completed_by": row.completed_by,
                "completed_by_username": row.completed_by_username
            })

        return success_response(
            data={
                "suggestions": suggestions,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        return error_response(message=f"获取建议列表失败: {str(e)}")


@router.put("/{suggestion_id}/complete", response_model=dict)
async def complete_suggestion(
    suggestion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记建议为已完成

    - 需要管理员权限
    """
    try:
        # 检查管理员权限
        if current_user.role != "admin":
            return error_response(
                message="无权限操作",
                code=403
            )

        # 检查建议是否存在
        check_result = await db.execute(text("""
            SELECT id, status FROM suggestions WHERE id = :id
        """), {"id": suggestion_id})

        suggestion = check_result.fetchone()
        if not suggestion:
            return error_response(message="建议不存在", code=404)

        if suggestion.status == "completed":
            return error_response(message="建议已经完成")

        # 更新状态
        await db.execute(text("""
            UPDATE suggestions
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                completed_by = :completed_by
            WHERE id = :id
        """), {
            "id": suggestion_id,
            "completed_by": current_user.id
        })
        await db.commit()

        return success_response(message="建议已标记为完成")
    except Exception as e:
        await db.rollback()
        return error_response(message=f"操作失败: {str(e)}")


@router.put("/{suggestion_id}/uncomplete", response_model=dict)
async def uncomplete_suggestion(
    suggestion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消完成标记

    - 需要管理员权限
    """
    try:
        # 检查管理员权限
        if current_user.role != "admin":
            return error_response(
                message="无权限操作",
                code=403
            )

        # 检查建议是否存在
        check_result = await db.execute(text("""
            SELECT id, status FROM suggestions WHERE id = :id
        """), {"id": suggestion_id})

        suggestion = check_result.fetchone()
        if not suggestion:
            return error_response(message="建议不存在", code=404)

        if suggestion.status == "pending":
            return error_response(message="建议未完成")

        # 更新状态
        await db.execute(text("""
            UPDATE suggestions
            SET status = 'pending',
                completed_at = NULL,
                completed_by = NULL
            WHERE id = :id
        """), {"id": suggestion_id})
        await db.commit()

        return success_response(message="已取消完成标记")
    except Exception as e:
        await db.rollback()
        return error_response(message=f"操作失败: {str(e)}")


@router.delete("/{suggestion_id}", response_model=dict)
async def delete_suggestion(
    suggestion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除建议

    - 创建者可以删除自己的建议
    - 管理员可以删除任何建议
    """
    try:
        # 检查建议是否存在
        check_result = await db.execute(text("""
            SELECT id, user_id FROM suggestions WHERE id = :id
        """), {"id": suggestion_id})

        suggestion = check_result.fetchone()
        if not suggestion:
            return error_response(message="建议不存在", code=404)

        # 检查权限
        if current_user.role != "admin" and suggestion.user_id != current_user.id:
            return error_response(
                message="无权限删除此建议",
                code=403
            )

        # 删除建议
        await db.execute(text("""
            DELETE FROM suggestions WHERE id = :id
        """), {"id": suggestion_id})
        await db.commit()

        return success_response(message="建议删除成功")
    except Exception as e:
        await db.rollback()
        return error_response(message=f"删除建议失败: {str(e)}")
