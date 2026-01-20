"""
标签相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete as sql_delete
from typing import List, Optional
from datetime import datetime

from app.models import get_db
from app.models.database import User, Tag, Paper, PaperTag
from app.schemas.tag import TagCreate, TagUpdate, TagResponse, TagListResponse, PaperTagCreate
from app.utils.dependencies import get_current_user, check_permission
from app.utils.response import success_response

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=dict)
async def create_tag(
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新标签

    - 需要登录
    - 自动关联到当前用户
    - 标签名称在用户范围内唯一
    """
    try:
        # 检查标签名是否已存在（用户范围内）
        existing_tag_query = select(Tag).where(
            and_(
                Tag.name == tag_data.name,
                Tag.created_by == current_user.id
            )
        )
        existing_tag_result = await db.execute(existing_tag_query)
        existing_tag = existing_tag_result.scalar_one_or_none()

        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签名称已存在"
            )

        # 创建标签
        new_tag = Tag(
            name=tag_data.name,
            color=tag_data.color,
            created_by=current_user.id
        )

        db.add(new_tag)
        await db.commit()
        await db.refresh(new_tag)

        # 构造响应
        tag_dict = {
            "id": new_tag.id,
            "name": new_tag.name,
            "color": new_tag.color,
            "created_by": new_tag.created_by,
            "created_at": new_tag.created_at,
            "updated_at": new_tag.updated_at,
            "paper_count": 0
        }

        return success_response(
            data=tag_dict,
            message="标签创建成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建标签失败: {str(e)}"
        )


@router.get("/", response_model=dict)
async def get_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有标签

    - 需要登录
    - 返回标签列表及每个标签关联的论文数量
    """
    try:
        # 查询用户的所有标签
        query = select(Tag).where(
            Tag.created_by == current_user.id
        ).order_by(Tag.created_at.desc())

        result = await db.execute(query)
        tags = result.scalars().all()

        # 为每个标签统计关联的论文数
        tags_list = []
        for tag in tags:
            # 统计该标签关联的论文数
            count_query = select(func.count(PaperTag.id)).where(
                PaperTag.tag_id == tag.id
            )
            count_result = await db.execute(count_query)
            paper_count = count_result.scalar() or 0

            tag_dict = {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "created_by": tag.created_by,
                "created_at": tag.created_at,
                "updated_at": tag.updated_at,
                "paper_count": paper_count
            }
            tags_list.append(tag_dict)

        return success_response(data={
            "total": len(tags_list),
            "tags": tags_list
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取标签列表失败: {str(e)}"
        )


@router.get("/{tag_id}", response_model=dict)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取标签详情

    - 需要登录
    - 只能查看自己创建的标签
    """
    try:
        # 查询标签
        query = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="标签不存在"
            )

        # 权限检查
        if not check_permission(current_user, tag.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此标签"
            )

        # 统计关联的论文数
        count_query = select(func.count(PaperTag.id)).where(
            PaperTag.tag_id == tag.id
        )
        count_result = await db.execute(count_query)
        paper_count = count_result.scalar() or 0

        tag_dict = {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "created_by": tag.created_by,
            "created_at": tag.created_at,
            "updated_at": tag.updated_at,
            "paper_count": paper_count
        }

        return success_response(data=tag_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取标签详情失败: {str(e)}"
        )


@router.put("/{tag_id}", response_model=dict)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新标签

    - 需要登录
    - 只能更新自己创建的标签
    """
    try:
        # 查询标签
        query = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="标签不存在"
            )

        # 权限检查
        if not check_permission(current_user, tag.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此标签"
            )

        # 如果要更新名称，检查是否重复
        if tag_data.name and tag_data.name != tag.name:
            existing_tag_query = select(Tag).where(
                and_(
                    Tag.name == tag_data.name,
                    Tag.created_by == current_user.id,
                    Tag.id != tag_id
                )
            )
            existing_tag_result = await db.execute(existing_tag_query)
            existing_tag = existing_tag_result.scalar_one_or_none()

            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="标签名称已存在"
                )

        # 更新字段
        update_data = tag_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)

        tag.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(tag)

        # 统计关联的论文数
        count_query = select(func.count(PaperTag.id)).where(
            PaperTag.tag_id == tag.id
        )
        count_result = await db.execute(count_query)
        paper_count = count_result.scalar() or 0

        tag_dict = {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "created_by": tag.created_by,
            "created_at": tag.created_at,
            "updated_at": tag.updated_at,
            "paper_count": paper_count
        }

        return success_response(
            data=tag_dict,
            message="标签更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新标签失败: {str(e)}"
        )


@router.delete("/{tag_id}", response_model=dict)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除标签

    - 需要登录
    - 只能删除自己创建的标签
    - 会同时删除该标签与论文的关联关系
    """
    try:
        # 查询标签
        query = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="标签不存在"
            )

        # 权限检查
        if not check_permission(current_user, tag.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此标签"
            )

        # 删除标签（会自动删除paper_tags中的关联记录）
        await db.delete(tag)
        await db.commit()

        return success_response(message="标签删除成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除标签失败: {str(e)}"
        )


@router.post("/papers/{paper_id}/tags", response_model=dict)
async def add_tags_to_paper(
    paper_id: int,
    tag_data: PaperTagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    为论文添加标签

    - 需要登录
    - 只能为自己的论文添加标签
    - 只能添加自己创建的标签
    - 已存在的标签-论文关联会被忽略
    """
    try:
        # 查询论文
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
        if not check_permission(current_user, paper.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此论文"
            )

        # 验证所有标签都存在且属于当前用户
        tags_query = select(Tag).where(
            and_(
                Tag.id.in_(tag_data.tag_ids),
                Tag.created_by == current_user.id
            )
        )
        tags_result = await db.execute(tags_query)
        tags = tags_result.scalars().all()

        if len(tags) != len(tag_data.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部分标签不存在或无权使用"
            )

        # 查询已存在的关联
        existing_query = select(PaperTag.tag_id).where(
            PaperTag.paper_id == paper_id
        )
        existing_result = await db.execute(existing_query)
        existing_tag_ids = set(existing_result.scalars().all())

        # 添加新的关联
        added_count = 0
        for tag_id in tag_data.tag_ids:
            if tag_id not in existing_tag_ids:
                paper_tag = PaperTag(
                    paper_id=paper_id,
                    tag_id=tag_id,
                    created_by=current_user.id
                )
                db.add(paper_tag)
                added_count += 1

        await db.commit()

        return success_response(
            data={"added_count": added_count},
            message=f"成功添加 {added_count} 个标签"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加标签失败: {str(e)}"
        )


@router.delete("/papers/{paper_id}/tags/{tag_id}", response_model=dict)
async def remove_tag_from_paper(
    paper_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    从论文移除标签

    - 需要登录
    - 只能移除自己论文的标签
    """
    try:
        # 查询论文
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
        if not check_permission(current_user, paper.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此论文"
            )

        # 删除关联
        delete_query = sql_delete(PaperTag).where(
            and_(
                PaperTag.paper_id == paper_id,
                PaperTag.tag_id == tag_id
            )
        )
        result = await db.execute(delete_query)
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="标签关联不存在"
            )

        return success_response(message="标签移除成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"移除标签失败: {str(e)}"
        )


@router.get("/papers/{paper_id}/tags", response_model=dict)
async def get_paper_tags(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取论文的所有标签

    - 需要登录
    """
    try:
        # 查询论文的所有标签
        query = select(Tag).join(
            PaperTag, Tag.id == PaperTag.tag_id
        ).where(
            PaperTag.paper_id == paper_id
        )

        result = await db.execute(query)
        tags = result.scalars().all()

        tags_list = []
        for tag in tags:
            tag_dict = {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "created_by": tag.created_by,
                "created_at": tag.created_at,
                "updated_at": tag.updated_at,
                "paper_count": 0  # 这里可以省略统计
            }
            tags_list.append(tag_dict)

        return success_response(data={
            "total": len(tags_list),
            "tags": tags_list
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取论文标签失败: {str(e)}"
        )
