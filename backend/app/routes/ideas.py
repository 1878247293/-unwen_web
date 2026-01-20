"""
想法（Ideas）管理API路由
用户可以记录和管理自己的研究想法、灵感和思考
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from datetime import datetime

from app.models.database import User
from app.models.db_session import get_db
from app.utils.dependencies import get_current_user
from app.utils.response import success_response, error_response


router = APIRouter()


def format_datetime(dt):
    """格式化日期时间为ISO格式字符串"""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)


@router.post("/", response_model=dict)
async def create_idea(
    title: Optional[str] = Query(None, max_length=200, description="想法标题"),
    references: Optional[str] = Query(None, max_length=2000, description="参考文献"),
    content: str = Query(..., min_length=1, max_length=10000, description="想法内容"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新想法

    - **title**: 想法标题（可选，最多200字符）
    - **references**: 参考文献（可选，最多2000字符）
    - **content**: 想法内容（必填，支持Markdown，最多10000字符）
    """
    try:
        # 插入想法
        query = text("""
            INSERT INTO ideas (user_id, title, "references", content, created_at, updated_at)
            VALUES (:user_id, :title, :references, :content, :created_at, :updated_at)
        """)

        now = datetime.utcnow()
        result = await db.execute(query, {
            "user_id": current_user.id,
            "title": title,
            "references": references,
            "content": content,
            "created_at": now,
            "updated_at": now
        })

        # 在 commit 之前获取插入的 ID
        idea_id = result.lastrowid
        await db.commit()

        # 查询完整想法信息
        idea_query = text("""
            SELECT id, user_id, title, "references", content, created_at, updated_at
            FROM ideas
            WHERE id = :id AND deleted_at IS NULL
        """)
        result = await db.execute(idea_query, {"id": idea_id})
        idea = result.fetchone()

        if not idea:
            return error_response("想法创建失败", 500)

        idea_dict = {
            "id": idea[0],
            "user_id": idea[1],
            "title": idea[2],
            "references": idea[3],
            "content": idea[4],
            "created_at": format_datetime(idea[5]),
            "updated_at": format_datetime(idea[6])
        }

        return success_response(data=idea_dict, message="想法创建成功")

    except Exception as e:
        await db.rollback()
        return error_response(f"创建失败: {str(e)}", 500)


@router.get("/", response_model=dict)
async def get_ideas(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的想法列表

    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **keyword**: 搜索关键词（搜索标题和内容）
    """
    try:
        # 构建WHERE子句
        where_clauses = ["user_id = :user_id", "deleted_at IS NULL"]
        params = {"user_id": current_user.id}

        # 搜索关键词
        if keyword:
            where_clauses.append("(title LIKE :keyword OR content LIKE :keyword)")
            params["keyword"] = f"%{keyword}%"

        where_clause = " AND ".join(where_clauses)

        # 查询总数
        count_query = text(f"""
            SELECT COUNT(*) FROM ideas
            WHERE {where_clause}
        """)
        result = await db.execute(count_query, params)
        total = result.scalar()

        # 查询想法列表
        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        ideas_query = text(f"""
            SELECT id, user_id, title, "references", content, created_at, updated_at
            FROM ideas
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)

        result = await db.execute(ideas_query, params)
        ideas = result.fetchall()

        ideas_list = []
        for idea in ideas:
            ideas_list.append({
                "id": idea[0],
                "user_id": idea[1],
                "title": idea[2],
                "references": idea[3],
                "content": idea[4],
                "content_preview": idea[4][:200] + "..." if len(idea[4]) > 200 else idea[4],
                "created_at": format_datetime(idea[5]),
                "updated_at": format_datetime(idea[6])
            })

        return success_response(data={
            "ideas": ideas_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        })

    except Exception as e:
        return error_response(f"获取失败: {str(e)}", 500)


@router.get("/{idea_id}", response_model=dict)
async def get_idea(
    idea_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取想法详情

    - **idea_id**: 想法ID
    """
    try:
        query = text("""
            SELECT id, user_id, title, "references", content, created_at, updated_at
            FROM ideas
            WHERE id = :id AND deleted_at IS NULL
        """)
        result = await db.execute(query, {"id": idea_id})
        idea = result.fetchone()

        if not idea:
            return error_response("想法不存在", 404)

        # 权限检查
        if idea[1] != current_user.id and current_user.role != "admin":
            return error_response("无权访问此想法", 403)

        idea_dict = {
            "id": idea[0],
            "user_id": idea[1],
            "title": idea[2],
            "references": idea[3],
            "content": idea[4],
            "created_at": format_datetime(idea[5]),
            "updated_at": format_datetime(idea[6])
        }

        return success_response(data=idea_dict)

    except Exception as e:
        return error_response(f"获取失败: {str(e)}", 500)


@router.put("/{idea_id}", response_model=dict)
async def update_idea(
    idea_id: int,
    title: Optional[str] = Query(None, max_length=200, description="想法标题"),
    references: Optional[str] = Query(None, max_length=2000, description="参考文献"),
    content: Optional[str] = Query(None, min_length=1, max_length=10000, description="想法内容"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新想法

    - **idea_id**: 想法ID
    - **title**: 新标题（可选）
    - **references**: 新参考文献（可选）
    - **content**: 新内容（可选）
    """
    try:
        # 查询想法
        query = text("""
            SELECT id, user_id FROM ideas
            WHERE id = :id AND deleted_at IS NULL
        """)
        result = await db.execute(query, {"id": idea_id})
        idea = result.fetchone()

        if not idea:
            return error_response("想法不存在", 404)

        # 权限检查
        if idea[1] != current_user.id and current_user.role != "admin":
            return error_response("无权修改此想法", 403)

        # 构建更新字段
        update_fields = []
        params = {"id": idea_id, "updated_at": datetime.utcnow()}

        if title is not None:
            update_fields.append("title = :title")
            params["title"] = title

        if references is not None:
            update_fields.append('"references" = :references')
            params["references"] = references

        if content is not None:
            update_fields.append("content = :content")
            params["content"] = content

        if not update_fields:
            return error_response("没有需要更新的字段", 400)

        update_fields.append("updated_at = :updated_at")

        # 更新想法
        update_query = text(f"""
            UPDATE ideas
            SET {", ".join(update_fields)}
            WHERE id = :id
        """)
        await db.execute(update_query, params)
        await db.commit()

        # 查询更新后的想法
        idea_query = text("""
            SELECT id, user_id, title, "references", content, created_at, updated_at
            FROM ideas
            WHERE id = :id
        """)
        result = await db.execute(idea_query, {"id": idea_id})
        updated_idea = result.fetchone()

        idea_dict = {
            "id": updated_idea[0],
            "user_id": updated_idea[1],
            "title": updated_idea[2],
            "references": updated_idea[3],
            "content": updated_idea[4],
            "created_at": format_datetime(updated_idea[5]),
            "updated_at": format_datetime(updated_idea[6])
        }

        return success_response(data=idea_dict, message="想法更新成功")

    except Exception as e:
        await db.rollback()
        return error_response(f"更新失败: {str(e)}", 500)


@router.delete("/{idea_id}", response_model=dict)
async def delete_idea(
    idea_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除想法（软删除）

    - **idea_id**: 想法ID
    """
    try:
        # 查询想法
        query = text("""
            SELECT id, user_id FROM ideas
            WHERE id = :id AND deleted_at IS NULL
        """)
        result = await db.execute(query, {"id": idea_id})
        idea = result.fetchone()

        if not idea:
            return error_response("想法不存在", 404)

        # 权限检查
        if idea[1] != current_user.id and current_user.role != "admin":
            return error_response("无权删除此想法", 403)

        # 软删除
        delete_query = text("""
            UPDATE ideas
            SET deleted_at = :deleted_at
            WHERE id = :id
        """)
        await db.execute(delete_query, {
            "id": idea_id,
            "deleted_at": datetime.utcnow()
        })
        await db.commit()

        return success_response(message="想法删除成功")

    except Exception as e:
        await db.rollback()
        return error_response(f"删除失败: {str(e)}", 500)
