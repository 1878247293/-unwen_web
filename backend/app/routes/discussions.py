"""
讨论管理相关的API路由 - 交流广场
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, or_
from typing import List, Optional
from datetime import datetime

from app.models import get_db
from app.models.database import Discussion, User, DiscussionLike, DiscussionFavorite, DiscussionReport, SystemSettings
from app.schemas.discussion import (
    DiscussionCreate,
    DiscussionUpdate,
    DiscussionResponse,
    DiscussionListResponse,
    DiscussionUser,
    ReportCreate,
    ReportResponse,
    ReportHandleRequest,
    SystemSettingUpdate
)
from app.utils.dependencies import get_current_user, get_current_admin_user
from app.utils.response import success_response, error_response
from app.routes.notifications import create_notification

router = APIRouter(prefix="/discussions", tags=["discussions"])


async def build_discussion_tree(
    discussions: List[Discussion],
    user_dict: dict,
    like_counts: dict,
    user_likes: set,
    user_favorites: set
) -> List[dict]:
    """构建讨论树结构（一级回复）"""
    # 分离顶层讨论和回复
    top_level = []
    replies_dict = {}

    for discussion in discussions:
        # 处理匿名用户
        if discussion.is_anonymous:
            user_info = {"id": None, "username": "匿名用户", "avatar": None}
        else:
            user_info = user_dict.get(discussion.user_id, {"id": discussion.user_id, "username": "Unknown", "avatar": None})

        discussion_dict = {
            "id": discussion.id,
            "user_id": discussion.user_id if not discussion.is_anonymous else None,
            "content": discussion.content,
            "is_anonymous": discussion.is_anonymous,
            "is_hidden": discussion.is_hidden,
            "parent_id": discussion.parent_id,
            "created_at": discussion.created_at,
            "updated_at": discussion.updated_at,
            "user": user_info,
            "like_count": like_counts.get(discussion.id, 0),
            "is_liked": discussion.id in user_likes,
            "is_favorited": discussion.id in user_favorites,
            "replies": [],
            "reply_count": 0
        }

        if discussion.parent_id is None:
            top_level.append(discussion_dict)
        else:
            if discussion.parent_id not in replies_dict:
                replies_dict[discussion.parent_id] = []
            replies_dict[discussion.parent_id].append(discussion_dict)

    # 将回复添加到父讨论
    for parent_discussion in top_level:
        if parent_discussion["id"] in replies_dict:
            parent_discussion["replies"] = replies_dict[parent_discussion["id"]]
            parent_discussion["reply_count"] = len(parent_discussion["replies"])

    return top_level


async def check_anonymous_allowed(db: AsyncSession) -> bool:
    """检查是否允许匿名发帖"""
    try:
        query = select(SystemSettings).where(SystemSettings.setting_key == "allow_anonymous_discussion")
        result = await db.execute(query)
        setting = result.scalar_one_or_none()

        if setting:
            return setting.setting_value.lower() in ["true", "1", "yes"]
        return False
    except Exception:
        return False


@router.post("/", response_model=dict)
async def create_discussion(
    discussion_data: DiscussionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建讨论/回复

    - 需要登录
    - 可以回复其他讨论（通过parent_id）
    - 支持匿名发布（需检查系统设置）
    - 自动关联到当前用户
    """
    try:
        # 如果是匿名发布，检查系统是否允许
        if discussion_data.is_anonymous:
            allowed = await check_anonymous_allowed(db)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="系统当前不允许匿名发布"
                )

        # 如果有parent_id，验证父讨论存在
        if discussion_data.parent_id:
            parent_query = select(Discussion).where(
                and_(
                    Discussion.id == discussion_data.parent_id,
                    Discussion.deleted_at.is_(None)
                )
            )
            parent_result = await db.execute(parent_query)
            parent_discussion = parent_result.scalar_one_or_none()

            if not parent_discussion:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父讨论不存在"
                )

            # 只允许一级回复，不允许回复的回复
            if parent_discussion.parent_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不支持多级回复，请回复顶层讨论"
                )

        # 创建讨论
        new_discussion = Discussion(
            user_id=current_user.id,
            content=discussion_data.content,
            is_anonymous=discussion_data.is_anonymous,
            parent_id=discussion_data.parent_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_discussion)
        await db.commit()
        await db.refresh(new_discussion)

        # 如果是回复讨论，创建通知
        if discussion_data.parent_id:
            # 获取父讨论信息
            parent_query = select(Discussion).where(Discussion.id == discussion_data.parent_id)
            parent_result = await db.execute(parent_query)
            parent_discussion = parent_result.scalar_one_or_none()

            # 只有在回复别人的讨论时才发送通知（不给自己发通知）
            if parent_discussion and parent_discussion.user_id != current_user.id and not parent_discussion.is_anonymous:
                # 创建通知
                notification_title = f"{current_user.username if not discussion_data.is_anonymous else '匿名用户'} 回复了你的讨论"
                notification_content = f"回复: {discussion_data.content[:100]}"
                notification_link = f"/discussions/{parent_discussion.id}"

                await create_notification(
                    db=db,
                    user_id=parent_discussion.user_id,
                    type="discussion_reply",
                    title=notification_title,
                    content=notification_content,
                    link=notification_link,
                    sender_id=current_user.id if not discussion_data.is_anonymous else None,
                    related_id=new_discussion.id
                )

        # 构造响应
        user_info = {
            "id": None if discussion_data.is_anonymous else current_user.id,
            "username": "匿名用户" if discussion_data.is_anonymous else current_user.username,
            "avatar": None if discussion_data.is_anonymous else current_user.avatar
        }

        discussion_dict = {
            "id": new_discussion.id,
            "user_id": None if discussion_data.is_anonymous else new_discussion.user_id,
            "content": new_discussion.content,
            "is_anonymous": new_discussion.is_anonymous,
            "is_hidden": new_discussion.is_hidden,
            "parent_id": new_discussion.parent_id,
            "created_at": new_discussion.created_at,
            "updated_at": new_discussion.updated_at,
            "user": user_info,
            "like_count": 0,
            "is_liked": False,
            "is_favorited": False,
            "replies": [],
            "reply_count": 0
        }

        return success_response(
            data=discussion_dict,
            message="讨论创建成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建讨论失败: {str(e)}"
        )


@router.get("/", response_model=dict)
async def get_discussions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("newest", description="排序方式：newest=最新，oldest=最早，hottest=最热（按点赞数）"),
    show_hidden: bool = Query(False, description="是否显示隐藏的讨论（仅管理员）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取讨论列表（包含回复）

    - 需要登录
    - 返回树形结构（顶层讨论+一级回复）
    - 支持分页和排序
    - 包含点赞数、是否点赞、是否收藏信息
    """
    try:
        # 构建基础查询条件
        base_conditions = [Discussion.deleted_at.is_(None)]

        # 只有管理员可以查看隐藏的讨论
        if not show_hidden or current_user.role != "admin":
            base_conditions.append(Discussion.is_hidden == False)

        # 查询所有讨论（包括回复）
        discussions_query = select(Discussion).where(and_(*base_conditions))

        # 排序
        if sort_by == "oldest":
            discussions_query = discussions_query.order_by(Discussion.created_at)
        elif sort_by == "hottest":
            # 按点赞数排序，需要JOIN
            discussions_query = (
                select(Discussion)
                .outerjoin(DiscussionLike, Discussion.id == DiscussionLike.discussion_id)
                .where(and_(*base_conditions))
                .group_by(Discussion.id)
                .order_by(desc(func.count(DiscussionLike.id)))
            )
        else:  # newest
            discussions_query = discussions_query.order_by(desc(Discussion.created_at))

        discussions_result = await db.execute(discussions_query)
        all_discussions = discussions_result.scalars().all()

        # 获取所有讨论的点赞数
        like_count_query = (
            select(
                DiscussionLike.discussion_id,
                func.count(DiscussionLike.id).label("count")
            )
            .group_by(DiscussionLike.discussion_id)
        )
        like_count_result = await db.execute(like_count_query)
        like_counts = {row.discussion_id: row.count for row in like_count_result}

        # 获取当前用户点赞的讨论
        user_likes_query = select(DiscussionLike.discussion_id).where(
            DiscussionLike.user_id == current_user.id
        )
        user_likes_result = await db.execute(user_likes_query)
        user_likes = set(row[0] for row in user_likes_result)

        # 获取当前用户收藏的讨论
        user_favorites_query = select(DiscussionFavorite.discussion_id).where(
            DiscussionFavorite.user_id == current_user.id
        )
        user_favorites_result = await db.execute(user_favorites_query)
        user_favorites = set(row[0] for row in user_favorites_result)

        # 获取所有讨论用户的信息（排除匿名用户）
        user_ids = list(set(
            discussion.user_id
            for discussion in all_discussions
            if not discussion.is_anonymous and discussion.user_id
        ))
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

        # 构建讨论树
        discussion_tree = await build_discussion_tree(
            all_discussions,
            user_dict,
            like_counts,
            user_likes,
            user_favorites
        )

        # 分页（只对顶层讨论分页）
        total = len(discussion_tree)
        offset = (page - 1) * page_size
        paginated_discussions = discussion_tree[offset:offset + page_size]

        return success_response(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "discussions": paginated_discussions
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取讨论列表失败: {str(e)}"
        )


@router.get("/favorites", response_model=dict)
async def get_user_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的收藏列表

    - 需要登录
    - 只返回用户收藏的讨论
    """
    try:
        # 查询用户收藏的讨论ID
        favorites_query = select(DiscussionFavorite.discussion_id).where(
            DiscussionFavorite.user_id == current_user.id
        )
        favorites_result = await db.execute(favorites_query)
        favorite_ids = [row[0] for row in favorites_result]

        if not favorite_ids:
            return success_response(
                data={
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "discussions": []
                }
            )

        # 查询收藏的讨论
        discussions_query = select(Discussion).where(
            and_(
                Discussion.id.in_(favorite_ids),
                Discussion.deleted_at.is_(None),
                Discussion.parent_id.is_(None)  # 只查询顶层讨论
            )
        ).order_by(desc(Discussion.created_at))

        discussions_result = await db.execute(discussions_query)
        discussions = discussions_result.scalars().all()

        # 获取点赞数
        like_count_query = (
            select(
                DiscussionLike.discussion_id,
                func.count(DiscussionLike.id).label("count")
            )
            .where(DiscussionLike.discussion_id.in_(favorite_ids))
            .group_by(DiscussionLike.discussion_id)
        )
        like_count_result = await db.execute(like_count_query)
        like_counts = {row.discussion_id: row.count for row in like_count_result}

        # 获取当前用户点赞的讨论
        user_likes_query = select(DiscussionLike.discussion_id).where(
            and_(
                DiscussionLike.user_id == current_user.id,
                DiscussionLike.discussion_id.in_(favorite_ids)
            )
        )
        user_likes_result = await db.execute(user_likes_query)
        user_likes = set(row[0] for row in user_likes_result)

        # 获取用户信息
        user_ids = list(set(
            discussion.user_id
            for discussion in discussions
            if not discussion.is_anonymous and discussion.user_id
        ))
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

        # 构建响应
        discussion_list = []
        for discussion in discussions:
            user_info = (
                {"id": None, "username": "匿名用户", "avatar": None}
                if discussion.is_anonymous
                else user_dict.get(discussion.user_id, {"id": discussion.user_id, "username": "Unknown", "avatar": None})
            )

            discussion_list.append({
                "id": discussion.id,
                "user_id": discussion.user_id if not discussion.is_anonymous else None,
                "content": discussion.content,
                "is_anonymous": discussion.is_anonymous,
                "is_hidden": discussion.is_hidden,
                "parent_id": discussion.parent_id,
                "created_at": discussion.created_at,
                "updated_at": discussion.updated_at,
                "user": user_info,
                "like_count": like_counts.get(discussion.id, 0),
                "is_liked": discussion.id in user_likes,
                "is_favorited": True,
                "replies": [],
                "reply_count": 0
            })

        # 分页
        total = len(discussion_list)
        offset = (page - 1) * page_size
        paginated_discussions = discussion_list[offset:offset + page_size]

        return success_response(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "discussions": paginated_discussions
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取收藏列表失败: {str(e)}"
        )


@router.get("/{discussion_id}", response_model=dict)
async def get_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个讨论详情

    - 需要登录
    """
    try:
        # 查询讨论
        query = select(Discussion).where(
            and_(
                Discussion.id == discussion_id,
                Discussion.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        discussion = result.scalar_one_or_none()

        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="讨论不存在"
            )

        # 如果讨论被隐藏，只有管理员可以查看
        if discussion.is_hidden and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="该讨论已被隐藏"
            )

        # 获取用户信息
        user_info = {"id": None, "username": "匿名用户", "avatar": None}
        if not discussion.is_anonymous and discussion.user_id:
            user_query = select(User).where(User.id == discussion.user_id)
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            if user:
                user_info = {"id": user.id, "username": user.username, "avatar": user.avatar}

        # 获取点赞数
        like_count_query = select(func.count(DiscussionLike.id)).where(
            DiscussionLike.discussion_id == discussion_id
        )
        like_count_result = await db.execute(like_count_query)
        like_count = like_count_result.scalar() or 0

        # 检查当前用户是否点赞
        is_liked_query = select(DiscussionLike).where(
            and_(
                DiscussionLike.discussion_id == discussion_id,
                DiscussionLike.user_id == current_user.id
            )
        )
        is_liked_result = await db.execute(is_liked_query)
        is_liked = is_liked_result.scalar_one_or_none() is not None

        # 检查当前用户是否收藏
        is_favorited_query = select(DiscussionFavorite).where(
            and_(
                DiscussionFavorite.discussion_id == discussion_id,
                DiscussionFavorite.user_id == current_user.id
            )
        )
        is_favorited_result = await db.execute(is_favorited_query)
        is_favorited = is_favorited_result.scalar_one_or_none() is not None

        # 获取回复
        replies_query = select(Discussion).where(
            and_(
                Discussion.parent_id == discussion_id,
                Discussion.deleted_at.is_(None)
            )
        ).order_by(Discussion.created_at)
        replies_result = await db.execute(replies_query)
        replies = replies_result.scalars().all()

        # 获取回复用户信息
        reply_user_ids = list(set(
            reply.user_id
            for reply in replies
            if not reply.is_anonymous and reply.user_id
        ))
        reply_users = {}
        if reply_user_ids:
            users_query = select(User).where(User.id.in_(reply_user_ids))
            users_result = await db.execute(users_query)
            users = users_result.scalars().all()
            reply_users = {
                u.id: {"id": u.id, "username": u.username, "avatar": u.avatar}
                for u in users
            }

        # 获取回复的点赞信息
        reply_ids = [reply.id for reply in replies]
        reply_like_counts = {}
        reply_user_likes = set()
        if reply_ids:
            reply_like_count_query = (
                select(
                    DiscussionLike.discussion_id,
                    func.count(DiscussionLike.id).label("count")
                )
                .where(DiscussionLike.discussion_id.in_(reply_ids))
                .group_by(DiscussionLike.discussion_id)
            )
            reply_like_count_result = await db.execute(reply_like_count_query)
            reply_like_counts = {row.discussion_id: row.count for row in reply_like_count_result}

            reply_user_likes_query = select(DiscussionLike.discussion_id).where(
                and_(
                    DiscussionLike.user_id == current_user.id,
                    DiscussionLike.discussion_id.in_(reply_ids)
                )
            )
            reply_user_likes_result = await db.execute(reply_user_likes_query)
            reply_user_likes = set(row[0] for row in reply_user_likes_result)

            reply_user_favorites_query = select(DiscussionFavorite.discussion_id).where(
                and_(
                    DiscussionFavorite.user_id == current_user.id,
                    DiscussionFavorite.discussion_id.in_(reply_ids)
                )
            )
            reply_user_favorites_result = await db.execute(reply_user_favorites_query)
            reply_user_favorites = set(row[0] for row in reply_user_favorites_result)
        else:
            reply_user_favorites = set()

        # 构造回复列表
        replies_list = []
        for reply in replies:
            reply_user_info = (
                {"id": None, "username": "匿名用户", "avatar": None}
                if reply.is_anonymous
                else reply_users.get(reply.user_id, {"id": reply.user_id, "username": "Unknown", "avatar": None})
            )

            replies_list.append({
                "id": reply.id,
                "user_id": reply.user_id if not reply.is_anonymous else None,
                "content": reply.content,
                "is_anonymous": reply.is_anonymous,
                "is_hidden": reply.is_hidden,
                "parent_id": reply.parent_id,
                "created_at": reply.created_at,
                "updated_at": reply.updated_at,
                "user": reply_user_info,
                "like_count": reply_like_counts.get(reply.id, 0),
                "is_liked": reply.id in reply_user_likes,
                "is_favorited": reply.id in reply_user_favorites,
                "replies": [],
                "reply_count": 0
            })

        # 构造响应
        discussion_dict = {
            "id": discussion.id,
            "user_id": discussion.user_id if not discussion.is_anonymous else None,
            "content": discussion.content,
            "is_anonymous": discussion.is_anonymous,
            "is_hidden": discussion.is_hidden,
            "parent_id": discussion.parent_id,
            "created_at": discussion.created_at,
            "updated_at": discussion.updated_at,
            "user": user_info,
            "like_count": like_count,
            "is_liked": is_liked,
            "is_favorited": is_favorited,
            "replies": replies_list,
            "reply_count": len(replies_list)
        }

        return success_response(data=discussion_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取讨论详情失败: {str(e)}"
        )


@router.put("/{discussion_id}", response_model=dict)
async def update_discussion(
    discussion_id: int,
    discussion_data: DiscussionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新讨论内容

    - 需要登录
    - 只能更新自己的讨论
    """
    try:
        # 查询讨论
        query = select(Discussion).where(
            and_(
                Discussion.id == discussion_id,
                Discussion.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        discussion = result.scalar_one_or_none()

        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="讨论不存在"
            )

        # 权限检查：只能修改自己的讨论
        if discussion.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此讨论"
            )

        # 更新讨论
        discussion.content = discussion_data.content
        discussion.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(discussion)

        # 获取用户信息
        user_info = {
            "id": None if discussion.is_anonymous else current_user.id,
            "username": "匿名用户" if discussion.is_anonymous else current_user.username,
            "avatar": None if discussion.is_anonymous else current_user.avatar
        }

        # 获取点赞和收藏信息
        like_count_query = select(func.count(DiscussionLike.id)).where(
            DiscussionLike.discussion_id == discussion_id
        )
        like_count_result = await db.execute(like_count_query)
        like_count = like_count_result.scalar() or 0

        is_liked_query = select(DiscussionLike).where(
            and_(
                DiscussionLike.discussion_id == discussion_id,
                DiscussionLike.user_id == current_user.id
            )
        )
        is_liked_result = await db.execute(is_liked_query)
        is_liked = is_liked_result.scalar_one_or_none() is not None

        is_favorited_query = select(DiscussionFavorite).where(
            and_(
                DiscussionFavorite.discussion_id == discussion_id,
                DiscussionFavorite.user_id == current_user.id
            )
        )
        is_favorited_result = await db.execute(is_favorited_query)
        is_favorited = is_favorited_result.scalar_one_or_none() is not None

        # 构造响应
        discussion_dict = {
            "id": discussion.id,
            "user_id": None if discussion.is_anonymous else discussion.user_id,
            "content": discussion.content,
            "is_anonymous": discussion.is_anonymous,
            "is_hidden": discussion.is_hidden,
            "parent_id": discussion.parent_id,
            "created_at": discussion.created_at,
            "updated_at": discussion.updated_at,
            "user": user_info,
            "like_count": like_count,
            "is_liked": is_liked,
            "is_favorited": is_favorited,
            "replies": [],
            "reply_count": 0
        }

        return success_response(
            data=discussion_dict,
            message="讨论更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新讨论失败: {str(e)}"
        )


@router.delete("/{discussion_id}", response_model=dict)
async def delete_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除讨论（软删除）

    - 需要登录
    - 只能删除自己的讨论或管理员可删除所有讨论
    - 删除讨论时会同时删除所有回复
    """
    try:
        # 查询讨论
        query = select(Discussion).where(
            and_(
                Discussion.id == discussion_id,
                Discussion.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        discussion = result.scalar_one_or_none()

        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="讨论不存在"
            )

        # 权限检查：只能删除自己的讨论或管理员可删除所有讨论
        if discussion.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此讨论"
            )

        # 软删除讨论
        discussion.deleted_at = datetime.utcnow()

        # 如果是顶层讨论，同时软删除所有回复
        if discussion.parent_id is None:
            replies_query = select(Discussion).where(
                and_(
                    Discussion.parent_id == discussion_id,
                    Discussion.deleted_at.is_(None)
                )
            )
            replies_result = await db.execute(replies_query)
            replies = replies_result.scalars().all()

            for reply in replies:
                reply.deleted_at = datetime.utcnow()

        await db.commit()

        return success_response(message="讨论删除成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除讨论失败: {str(e)}"
        )


@router.post("/{discussion_id}/like", response_model=dict)
async def like_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    点赞讨论

    - 需要登录
    - 不能重复点赞
    """
    try:
        # 检查讨论是否存在
        discussion_query = select(Discussion).where(
            and_(
                Discussion.id == discussion_id,
                Discussion.deleted_at.is_(None)
            )
        )
        discussion_result = await db.execute(discussion_query)
        discussion = discussion_result.scalar_one_or_none()

        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="讨论不存在"
            )

        # 检查是否已点赞
        like_query = select(DiscussionLike).where(
            and_(
                DiscussionLike.discussion_id == discussion_id,
                DiscussionLike.user_id == current_user.id
            )
        )
        like_result = await db.execute(like_query)
        existing_like = like_result.scalar_one_or_none()

        if existing_like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已经点赞过该讨论"
            )

        # 创建点赞
        new_like = DiscussionLike(
            discussion_id=discussion_id,
            user_id=current_user.id,
            created_at=datetime.utcnow()
        )

        db.add(new_like)
        await db.commit()

        # 如果不是自己的讨论且不是匿名讨论，创建通知
        if discussion.user_id != current_user.id and not discussion.is_anonymous:
            notification_title = f"{current_user.username} 点赞了你的讨论"
            notification_content = f"点赞: {discussion.content[:100]}"
            notification_link = f"/discussions/{discussion_id}"

            await create_notification(
                db=db,
                user_id=discussion.user_id,
                type="discussion_like",
                title=notification_title,
                content=notification_content,
                link=notification_link,
                sender_id=current_user.id,
                related_id=discussion_id
            )

        return success_response(message="点赞成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"点赞失败: {str(e)}"
        )


@router.delete("/{discussion_id}/like", response_model=dict)
async def unlike_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消点赞讨论

    - 需要登录
    """
    try:
        # 查询点赞记录
        like_query = select(DiscussionLike).where(
            and_(
                DiscussionLike.discussion_id == discussion_id,
                DiscussionLike.user_id == current_user.id
            )
        )
        like_result = await db.execute(like_query)
        like = like_result.scalar_one_or_none()

        if not like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到点赞记录"
            )

        # 删除点赞
        await db.delete(like)
        await db.commit()

        return success_response(message="取消点赞成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消点赞失败: {str(e)}"
        )


@router.post("/{discussion_id}/favorite", response_model=dict)
async def favorite_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    收藏讨论

    - 需要登录
    - 不能重复收藏
    """
    try:
        # 检查讨论是否存在
        discussion_query = select(Discussion).where(
            and_(
                Discussion.id == discussion_id,
                Discussion.deleted_at.is_(None)
            )
        )
        discussion_result = await db.execute(discussion_query)
        discussion = discussion_result.scalar_one_or_none()

        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="讨论不存在"
            )

        # 检查是否已收藏
        favorite_query = select(DiscussionFavorite).where(
            and_(
                DiscussionFavorite.discussion_id == discussion_id,
                DiscussionFavorite.user_id == current_user.id
            )
        )
        favorite_result = await db.execute(favorite_query)
        existing_favorite = favorite_result.scalar_one_or_none()

        if existing_favorite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已经收藏过该讨论"
            )

        # 创建收藏
        new_favorite = DiscussionFavorite(
            discussion_id=discussion_id,
            user_id=current_user.id,
            created_at=datetime.utcnow()
        )

        db.add(new_favorite)
        await db.commit()

        return success_response(message="收藏成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"收藏失败: {str(e)}"
        )


@router.delete("/{discussion_id}/favorite", response_model=dict)
async def unfavorite_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消收藏讨论

    - 需要登录
    """
    try:
        # 查询收藏记录
        favorite_query = select(DiscussionFavorite).where(
            and_(
                DiscussionFavorite.discussion_id == discussion_id,
                DiscussionFavorite.user_id == current_user.id
            )
        )
        favorite_result = await db.execute(favorite_query)
        favorite = favorite_result.scalar_one_or_none()

        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到收藏记录"
            )

        # 删除收藏
        await db.delete(favorite)
        await db.commit()

        return success_response(message="取消收藏成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消收藏失败: {str(e)}"
        )


@router.post("/{discussion_id}/report", response_model=dict)
async def report_discussion(
    discussion_id: int,
    report_data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    举报讨论

    - 需要登录
    - 可以重复举报（每次都会创建新的举报记录）
    """
    try:
        # 检查讨论是否存在
        discussion_query = select(Discussion).where(
            and_(
                Discussion.id == discussion_id,
                Discussion.deleted_at.is_(None)
            )
        )
        discussion_result = await db.execute(discussion_query)
        discussion = discussion_result.scalar_one_or_none()

        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="讨论不存在"
            )

        # 创建举报
        new_report = DiscussionReport(
            discussion_id=discussion_id,
            user_id=current_user.id,
            reason=report_data.reason,
            status="pending",
            created_at=datetime.utcnow()
        )

        db.add(new_report)
        await db.commit()

        return success_response(message="举报成功，管理员会尽快处理")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"举报失败: {str(e)}"
        )


@router.get("/reports", response_model=dict)
async def get_reports(
    status_filter: Optional[str] = Query(None, description="筛选状态：pending, handled, rejected"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取所有举报记录（管理员专用）

    - 需要管理员权限
    - 支持按状态筛选
    """
    try:
        # 构建查询条件
        conditions = []
        if status_filter:
            conditions.append(DiscussionReport.status == status_filter)

        # 查询总数
        count_query = select(func.count(DiscussionReport.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = count_result.scalar()

        # 查询举报列表
        reports_query = select(DiscussionReport)
        if conditions:
            reports_query = reports_query.where(and_(*conditions))
        reports_query = reports_query.order_by(desc(DiscussionReport.created_at))
        reports_query = reports_query.offset((page - 1) * page_size).limit(page_size)

        reports_result = await db.execute(reports_query)
        reports = reports_result.scalars().all()

        # 获取相关用户信息
        user_ids = set()
        for report in reports:
            user_ids.add(report.user_id)
            if report.handled_by:
                user_ids.add(report.handled_by)

        user_dict = {}
        if user_ids:
            users_query = select(User).where(User.id.in_(list(user_ids)))
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

        # 构造响应
        reports_list = []
        for report in reports:
            reports_list.append({
                "id": report.id,
                "discussion_id": report.discussion_id,
                "user_id": report.user_id,
                "reason": report.reason,
                "status": report.status,
                "created_at": report.created_at,
                "handled_at": report.handled_at,
                "handled_by": report.handled_by,
                "reporter": user_dict.get(report.user_id),
                "handler": user_dict.get(report.handled_by) if report.handled_by else None
            })

        return success_response(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "reports": reports_list
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取举报列表失败: {str(e)}"
        )


@router.put("/reports/{report_id}/handle", response_model=dict)
async def handle_report(
    report_id: int,
    handle_data: ReportHandleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    处理举报（管理员专用）

    - 需要管理员权限
    - 可以设置状态为 handled（已处理）或 rejected（已驳回）
    """
    try:
        # 验证状态值
        if handle_data.status not in ["handled", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的状态值，只能是 handled 或 rejected"
            )

        # 查询举报
        report_query = select(DiscussionReport).where(DiscussionReport.id == report_id)
        report_result = await db.execute(report_query)
        report = report_result.scalar_one_or_none()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="举报不存在"
            )

        # 更新举报状态
        report.status = handle_data.status
        report.handled_at = datetime.utcnow()
        report.handled_by = current_user.id

        await db.commit()

        return success_response(message="举报处理成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理举报失败: {str(e)}"
        )


@router.put("/{discussion_id}/hide", response_model=dict)
async def hide_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    隐藏讨论（管理员专用）

    - 需要管理员权限
    - 隐藏后普通用户无法查看
    """
    try:
        # 查询讨论
        discussion_query = select(Discussion).where(
            and_(
                Discussion.id == discussion_id,
                Discussion.deleted_at.is_(None)
            )
        )
        discussion_result = await db.execute(discussion_query)
        discussion = discussion_result.scalar_one_or_none()

        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="讨论不存在"
            )

        # 设置为隐藏
        discussion.is_hidden = True
        discussion.updated_at = datetime.utcnow()

        await db.commit()

        return success_response(message="讨论已隐藏")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"隐藏讨论失败: {str(e)}"
        )


@router.put("/{discussion_id}/unhide", response_model=dict)
async def unhide_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    取消隐藏讨论（管理员专用）

    - 需要管理员权限
    """
    try:
        # 查询讨论
        discussion_query = select(Discussion).where(
            and_(
                Discussion.id == discussion_id,
                Discussion.deleted_at.is_(None)
            )
        )
        discussion_result = await db.execute(discussion_query)
        discussion = discussion_result.scalar_one_or_none()

        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="讨论不存在"
            )

        # 取消隐藏
        discussion.is_hidden = False
        discussion.updated_at = datetime.utcnow()

        await db.commit()

        return success_response(message="讨论已取消隐藏")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消隐藏讨论失败: {str(e)}"
        )


@router.get("/admin/settings/anonymous", response_model=dict)
async def get_anonymous_setting(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取匿名发帖设置

    - 所有登录用户可查看
    """
    try:
        query = select(SystemSettings).where(SystemSettings.setting_key == "allow_anonymous_discussion")
        result = await db.execute(query)
        setting = result.scalar_one_or_none()

        if not setting:
            # 如果设置不存在，返回默认值 false
            return success_response(
                data={
                    "setting_key": "allow_anonymous_discussion",
                    "setting_value": "false",
                    "description": "是否允许匿名发布讨论"
                }
            )

        return success_response(
            data={
                "setting_key": setting.setting_key,
                "setting_value": setting.setting_value,
                "description": setting.description
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设置失败: {str(e)}"
        )


@router.put("/admin/settings/anonymous", response_model=dict)
async def update_anonymous_setting(
    setting_data: SystemSettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    更新匿名发帖设置（管理员专用）

    - 需要管理员权限
    - setting_value 应为 "true" 或 "false"
    """
    try:
        # 验证值
        if setting_data.setting_value.lower() not in ["true", "false", "1", "0", "yes", "no"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的设置值，应为 true 或 false"
            )

        # 标准化值为 true 或 false
        normalized_value = "true" if setting_data.setting_value.lower() in ["true", "1", "yes"] else "false"

        # 查询设置是否存在
        query = select(SystemSettings).where(SystemSettings.setting_key == "allow_anonymous_discussion")
        result = await db.execute(query)
        setting = result.scalar_one_or_none()

        if setting:
            # 更新现有设置
            setting.setting_value = normalized_value
            setting.updated_at = datetime.utcnow()
        else:
            # 创建新设置
            setting = SystemSettings(
                setting_key="allow_anonymous_discussion",
                setting_value=normalized_value,
                description="是否允许匿名发布讨论",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(setting)

        await db.commit()
        await db.refresh(setting)

        return success_response(
            data={
                "setting_key": setting.setting_key,
                "setting_value": setting.setting_value,
                "description": setting.description
            },
            message="设置更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新设置失败: {str(e)}"
        )
