"""
评论管理相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from typing import List, Optional
from datetime import datetime

from app.models import get_db
from app.models.database import Comment, Paper, User
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentListResponse,
    CommentUser
)
from app.utils.dependencies import get_current_user, check_permission
from app.utils.response import success_response, error_response
from app.routes.notifications import create_notification

router = APIRouter(prefix="/comments", tags=["comments"])


async def build_comment_tree(comments: List[Comment], user_dict: dict) -> List[dict]:
    """构建评论树结构（一级回复）"""
    # 分离顶层评论和回复
    top_level = []
    replies_dict = {}

    for comment in comments:
        comment_dict = {
            "id": comment.id,
            "paper_id": comment.paper_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "parent_id": comment.parent_id,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "user": user_dict.get(comment.user_id, {"id": comment.user_id, "username": "Unknown"}),
            "replies": [],
            "reply_count": 0
        }

        if comment.parent_id is None:
            top_level.append(comment_dict)
        else:
            if comment.parent_id not in replies_dict:
                replies_dict[comment.parent_id] = []
            replies_dict[comment.parent_id].append(comment_dict)

    # 将回复添加到父评论
    for parent_comment in top_level:
        if parent_comment["id"] in replies_dict:
            parent_comment["replies"] = replies_dict[parent_comment["id"]]
            parent_comment["reply_count"] = len(parent_comment["replies"])

    return top_level


@router.post("/papers/{paper_id}", response_model=dict)
async def create_comment(
    paper_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    为论文创建评论

    - 需要登录
    - 可以回复其他评论（通过parent_id）
    - 自动关联到当前用户
    """
    try:
        # 验证论文存在且用户有权访问
        paper_query = select(Paper).where(
            and_(
                Paper.id == paper_id,
                Paper.deleted_at.is_(None)
            )
        )
        paper_result = await db.execute(paper_query)
        paper = paper_result.scalar_one_or_none()

        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文不存在"
            )

        # 权限检查：用户必须能访问此论文才能评论
        if current_user.role != "admin":
            if paper.created_by != current_user.id and not paper.is_shared:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问此论文"
                )

        # 如果有parent_id，验证父评论存在且属于同一论文
        if comment_data.parent_id:
            parent_query = select(Comment).where(
                and_(
                    Comment.id == comment_data.parent_id,
                    Comment.paper_id == paper_id,
                    Comment.deleted_at.is_(None)
                )
            )
            parent_result = await db.execute(parent_query)
            parent_comment = parent_result.scalar_one_or_none()

            if not parent_comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父评论不存在"
                )

            # 只允许一级回复，不允许回复的回复
            if parent_comment.parent_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不支持多级回复，请回复顶层评论"
                )

        # 创建评论
        new_comment = Comment(
            paper_id=paper_id,
            user_id=current_user.id,
            content=comment_data.content,
            parent_id=comment_data.parent_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)

        # 如果是回复评论，创建通知
        if comment_data.parent_id:
            # 获取父评论信息
            parent_query = select(Comment).where(Comment.id == comment_data.parent_id)
            parent_result = await db.execute(parent_query)
            parent_comment = parent_result.scalar_one_or_none()

            # 只有在回复别人的评论时才发送通知（不给自己发通知）
            if parent_comment and parent_comment.user_id != current_user.id:
                # 创建通知
                notification_title = f"{current_user.username} 回复了你的评论"
                notification_content = f"在论文《{paper.title}》中回复: {comment_data.content[:100]}"
                notification_link = f"/papers/{paper_id}"

                await create_notification(
                    db=db,
                    user_id=parent_comment.user_id,
                    type="comment_reply",
                    title=notification_title,
                    content=notification_content,
                    link=notification_link,
                    sender_id=current_user.id,
                    related_id=new_comment.id
                )

        # 构造响应
        comment_dict = {
            "id": new_comment.id,
            "paper_id": new_comment.paper_id,
            "user_id": new_comment.user_id,
            "content": new_comment.content,
            "parent_id": new_comment.parent_id,
            "created_at": new_comment.created_at,
            "updated_at": new_comment.updated_at,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "avatar": current_user.avatar
            },
            "replies": [],
            "reply_count": 0
        }

        return success_response(
            data=comment_dict,
            message="评论创建成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建评论失败: {str(e)}"
        )


@router.get("/papers/{paper_id}", response_model=dict)
async def get_paper_comments(
    paper_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_order: str = Query("desc", description="排序方向（desc=最新在前，asc=最早在前）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取论文的评论列表（包含回复）

    - 需要登录
    - 返回树形结构（顶层评论+一级回复）
    - 支持分页和排序
    """
    try:
        # 验证论文存在且用户有权访问
        paper_query = select(Paper).where(
            and_(
                Paper.id == paper_id,
                Paper.deleted_at.is_(None)
            )
        )
        paper_result = await db.execute(paper_query)
        paper = paper_result.scalar_one_or_none()

        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文不存在"
            )

        # 权限检查
        if current_user.role != "admin":
            if paper.created_by != current_user.id and not paper.is_shared:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问此论文"
                )

        # 查询所有评论（包括回复）
        comments_query = select(Comment).where(
            and_(
                Comment.paper_id == paper_id,
                Comment.deleted_at.is_(None)
            )
        )

        # 按创建时间排序
        if sort_order == "desc":
            comments_query = comments_query.order_by(desc(Comment.created_at))
        else:
            comments_query = comments_query.order_by(Comment.created_at)

        comments_result = await db.execute(comments_query)
        all_comments = comments_result.scalars().all()

        # 获取所有评论用户的信息
        user_ids = list(set(comment.user_id for comment in all_comments))
        user_dict = {}
        if user_ids:
            users_query = select(User).where(User.id.in_(user_ids))
            users_result = await db.execute(users_query)
            users = users_result.scalars().all()
            user_dict = {
                user.id: {
                    "id": user.id,
                    "username": user.username,
                    "avatar": user.avatar
                }
                for user in users
            }

        # 构建评论树
        comment_tree = await build_comment_tree(all_comments, user_dict)

        # 分页（只对顶层评论分页）
        total = len(comment_tree)
        offset = (page - 1) * page_size
        paginated_comments = comment_tree[offset:offset + page_size]

        return success_response(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "comments": paginated_comments
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评论列表失败: {str(e)}"
        )


@router.get("/{comment_id}", response_model=dict)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个评论详情

    - 需要登录
    """
    try:
        # 查询评论
        query = select(Comment).where(
            and_(
                Comment.id == comment_id,
                Comment.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )

        # 查询评论所属论文并验证权限
        paper_query = select(Paper).where(Paper.id == comment.paper_id)
        paper_result = await db.execute(paper_query)
        paper = paper_result.scalar_one_or_none()

        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文不存在"
            )

        # 权限检查
        if current_user.role != "admin":
            if paper.created_by != current_user.id and not paper.is_shared:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问此评论"
                )

        # 获取用户信息
        user_query = select(User).where(User.id == comment.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        # 获取回复
        replies_query = select(Comment).where(
            and_(
                Comment.parent_id == comment_id,
                Comment.deleted_at.is_(None)
            )
        ).order_by(Comment.created_at)
        replies_result = await db.execute(replies_query)
        replies = replies_result.scalars().all()

        # 获取回复用户信息
        reply_user_ids = list(set(reply.user_id for reply in replies))
        reply_users = {}
        if reply_user_ids:
            users_query = select(User).where(User.id.in_(reply_user_ids))
            users_result = await db.execute(users_query)
            users = users_result.scalars().all()
            reply_users = {
                u.id: {"id": u.id, "username": u.username, "avatar": u.avatar}
                for u in users
            }

        # 构造回复列表
        replies_list = [
            {
                "id": reply.id,
                "paper_id": reply.paper_id,
                "user_id": reply.user_id,
                "content": reply.content,
                "parent_id": reply.parent_id,
                "created_at": reply.created_at,
                "updated_at": reply.updated_at,
                "user": reply_users.get(reply.user_id, {"id": reply.user_id, "username": "Unknown"}),
                "replies": [],
                "reply_count": 0
            }
            for reply in replies
        ]

        # 构造响应
        comment_dict = {
            "id": comment.id,
            "paper_id": comment.paper_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "parent_id": comment.parent_id,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "user": {
                "id": user.id,
                "username": user.username,
                "avatar": user.avatar
            } if user else {"id": comment.user_id, "username": "Unknown"},
            "replies": replies_list,
            "reply_count": len(replies_list)
        }

        return success_response(data=comment_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评论详情失败: {str(e)}"
        )


@router.put("/{comment_id}", response_model=dict)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新评论内容

    - 需要登录
    - 只能更新自己的评论
    """
    try:
        # 查询评论
        query = select(Comment).where(
            and_(
                Comment.id == comment_id,
                Comment.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )

        # 权限检查：只能修改自己的评论
        if comment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此评论"
            )

        # 更新评论
        comment.content = comment_data.content
        comment.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(comment)

        # 构造响应
        comment_dict = {
            "id": comment.id,
            "paper_id": comment.paper_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "parent_id": comment.parent_id,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "avatar": current_user.avatar
            },
            "replies": [],
            "reply_count": 0
        }

        return success_response(
            data=comment_dict,
            message="评论更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新评论失败: {str(e)}"
        )


@router.delete("/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除评论（软删除）

    - 需要登录
    - 只能删除自己的评论或管理员可删除所有评论
    - 删除评论时会同时删除所有回复
    """
    try:
        # 查询评论
        query = select(Comment).where(
            and_(
                Comment.id == comment_id,
                Comment.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )

        # 权限检查：只能删除自己的评论或管理员可删除所有评论
        if comment.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此评论"
            )

        # 软删除评论
        comment.deleted_at = datetime.utcnow()

        # 如果是顶层评论，同时软删除所有回复
        if comment.parent_id is None:
            replies_query = select(Comment).where(
                and_(
                    Comment.parent_id == comment_id,
                    Comment.deleted_at.is_(None)
                )
            )
            replies_result = await db.execute(replies_query)
            replies = replies_result.scalars().all()

            for reply in replies:
                reply.deleted_at = datetime.utcnow()

        await db.commit()

        return success_response(message="评论删除成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除评论失败: {str(e)}"
        )
