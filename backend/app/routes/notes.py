"""
笔记管理相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from typing import List
from datetime import datetime, timezone

from app.models import get_db
from app.models.database import Note, Paper, User
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse
from app.utils.dependencies import get_current_user, check_permission
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/papers/{paper_id}/notes", response_model=dict)
async def create_note(
    paper_id: int,
    note_data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    为论文创建笔记

    - 需要登录
    - 自动关联到当前用户
    """
    try:
        # 验证论文存在
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

        # 创建笔记
        new_note = Note(
            **note_data.model_dump(),
            paper_id=paper_id,
            created_by=current_user.id
        )

        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)

        # 更新论文的notes_preview字段（取前200字符）
        preview = note_data.content[:200] if len(note_data.content) > 200 else note_data.content
        paper.notes_preview = preview
        paper.updated_at = datetime.utcnow()
        await db.commit()

        # 构造响应
        note_dict = {
            "id": new_note.id,
            "paper_id": new_note.paper_id,
            "title": new_note.title,
            "content": new_note.content,
            "note_type": new_note.note_type,
            "created_by": new_note.created_by,
            "created_at": new_note.created_at,
            "updated_at": new_note.updated_at,
            "creator_name": current_user.username
        }

        return success_response(
            data=note_dict,
            message="笔记创建成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建笔记失败: {str(e)}"
        )


@router.get("/papers/{paper_id}/notes", response_model=dict)
async def get_paper_notes(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取论文的所有笔记

    - 需要登录
    - 按创建时间倒序排列
    """
    try:
        # 验证论文存在且有权访问
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
                detail="无权访问此论文"
            )

        # 查询笔记
        notes_query = select(Note).where(
            and_(
                Note.paper_id == paper_id,
                Note.deleted_at.is_(None)
            )
        ).order_by(desc(Note.created_at))

        result = await db.execute(notes_query)
        notes = result.scalars().all()

        # 获取创建者信息
        user_ids = list(set(note.created_by for note in notes))
        users = {}
        if user_ids:
            users_query = select(User).where(User.id.in_(user_ids))
            users_result = await db.execute(users_query)
            users = {user.id: user.username for user in users_result.scalars().all()}

        # 构造响应
        notes_list = [
            {
                "id": note.id,
                "paper_id": note.paper_id,
                "title": note.title,
                "content": note.content,
                "note_type": note.note_type,
                "created_by": note.created_by,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
                "creator_name": users.get(note.created_by)
            }
            for note in notes
        ]

        return success_response(
            data={
                "total": len(notes_list),
                "notes": notes_list
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取笔记列表失败: {str(e)}"
        )


@router.get("/{note_id}", response_model=dict)
async def get_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取笔记详情

    - 需要登录
    - 只能查看自己的笔记或有权访问的论文的笔记
    """
    try:
        # 查询笔记
        query = select(Note).where(
            and_(
                Note.id == note_id,
                Note.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        note = result.scalar_one_or_none()

        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在"
            )

        # 查询关联的论文以检查权限
        paper_query = select(Paper).where(Paper.id == note.paper_id)
        paper_result = await db.execute(paper_query)
        paper = paper_result.scalar_one_or_none()

        if paper and not check_permission(current_user, paper.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此笔记"
            )

        # 获取创建者信息
        user_query = select(User).where(User.id == note.created_by)
        user_result = await db.execute(user_query)
        creator = user_result.scalar_one_or_none()

        # 构造响应
        note_dict = {
            "id": note.id,
            "paper_id": note.paper_id,
            "title": note.title,
            "content": note.content,
            "note_type": note.note_type,
            "created_by": note.created_by,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
            "creator_name": creator.username if creator else None
        }

        return success_response(data=note_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取笔记详情失败: {str(e)}"
        )


@router.put("/{note_id}", response_model=dict)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新笔记

    - 需要登录
    - 只能更新自己创建的笔记
    """
    try:
        # 查询笔记
        query = select(Note).where(
            and_(
                Note.id == note_id,
                Note.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        note = result.scalar_one_or_none()

        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在"
            )

        # 权限检查
        if not check_permission(current_user, note.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此笔记"
            )

        # 更新字段
        update_data = note_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(note, field, value)

        note.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(note)

        # 如果有内容更新，同时更新论文的notes_preview
        if 'content' in update_data:
            paper_query = select(Paper).where(Paper.id == note.paper_id)
            paper_result = await db.execute(paper_query)
            paper = paper_result.scalar_one_or_none()

            if paper:
                preview = note.content[:200] if len(note.content) > 200 else note.content
                paper.notes_preview = preview
                paper.updated_at = datetime.utcnow()
                await db.commit()

        # 构造响应
        note_dict = {
            "id": note.id,
            "paper_id": note.paper_id,
            "title": note.title,
            "content": note.content,
            "note_type": note.note_type,
            "created_by": note.created_by,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
            "creator_name": current_user.username
        }

        return success_response(
            data=note_dict,
            message="笔记更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新笔记失败: {str(e)}"
        )


@router.delete("/{note_id}", response_model=dict)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除笔记（软删除）

    - 需要登录
    - 只能删除自己创建的笔记
    """
    try:
        # 查询笔记
        query = select(Note).where(
            and_(
                Note.id == note_id,
                Note.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        note = result.scalar_one_or_none()

        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在"
            )

        # 权限检查
        if not check_permission(current_user, note.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此笔记"
            )

        # 软删除
        note.deleted_at = datetime.utcnow()
        note.updated_at = datetime.utcnow()

        await db.commit()

        return success_response(message="笔记删除成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除笔记失败: {str(e)}"
        )


@router.get("/{note_id}/export", response_class=Response)
async def export_note(
    note_id: int,
    format: str = "md",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出笔记为Markdown格式

    - 需要登录
    - 只能导出自己的笔记或管理员可导出所有笔记
    - 支持格式：md/markdown
    """
    try:
        # 查询笔记
        note_query = select(Note).where(
            and_(
                Note.id == note_id,
                Note.deleted_at.is_(None)
            )
        )
        note_result = await db.execute(note_query)
        note = note_result.scalar_one_or_none()

        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在"
            )

        # 权限检查：只能导出自己的笔记，或者管理员可以导出所有笔记
        if note.created_by != current_user.id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权导出此笔记"
            )

        # 查询关联的论文信息
        paper_query = select(Paper).where(Paper.id == note.paper_id)
        paper_result = await db.execute(paper_query)
        paper = paper_result.scalar_one_or_none()

        # 生成Markdown内容
        note_type_map = {
            'summary': '摘要',
            'method': '方法论',
            'experiment': '实验结果',
            'conclusion': '结论',
            'question': '问题',
            'idea': '想法',
            'other': '其他'
        }

        markdown_content = f"""# {note.title or '无标题'}

**类型**: {note_type_map.get(note.note_type, note.note_type)}
**创建时间**: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}
**更新时间**: {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
"""

        # 添加论文信息（如果有）
        if paper:
            markdown_content += f"""**关联论文**: {paper.title}
"""
            if paper.authors:
                markdown_content += f"""**作者**: {paper.authors}
"""
            if paper.year:
                markdown_content += f"""**年份**: {paper.year}
"""

        markdown_content += f"""
---

## 内容

{note.content}

---

*导出时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""

        # 生成文件名
        filename = f"note_{note_id}_{note.title or 'untitled'}.md"
        # 处理文件名中的特殊字符
        filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.')).rstrip()

        # 返回文件响应
        return Response(
            content=markdown_content.encode('utf-8'),
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出笔记失败: {str(e)}"
        )
