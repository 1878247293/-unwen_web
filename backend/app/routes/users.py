"""
用户相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text
from datetime import datetime
from pydantic import BaseModel

from app.models import get_db
from app.models.database import User, Paper, Note, Tag, ReadingHistory
from app.schemas.user import UserResponse, UserUpdate, UserPasswordUpdate
from app.utils.dependencies import get_current_user, get_current_admin_user
from app.utils.security import get_password_hash, verify_password
from app.utils.response import success_response

router = APIRouter()


class UserRoleUpdate(BaseModel):
    """更新用户角色"""
    role: str

class PasswordResetRequest(BaseModel):
    """重置密码请求"""
    new_password: str


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    user_response = UserResponse.model_validate(current_user)
    return success_response(data=user_response.model_dump())


@router.get("/me/stats", response_model=dict)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的统计信息"""
    try:
        # 统计论文数量
        papers_query = text(
            "SELECT COUNT(*) FROM papers WHERE created_by = :user_id AND deleted_at IS NULL"
        )
        papers_result = await db.execute(papers_query, {"user_id": current_user.id})
        total_papers = papers_result.scalar()

        # 统计笔记数量
        notes_query = text(
            "SELECT COUNT(*) FROM notes WHERE created_by = :user_id AND deleted_at IS NULL"
        )
        notes_result = await db.execute(notes_query, {"user_id": current_user.id})
        total_notes = notes_result.scalar()

        # 统计标签数量
        tags_query = text(
            "SELECT COUNT(*) FROM tags WHERE created_by = :user_id"
        )
        tags_result = await db.execute(tags_query, {"user_id": current_user.id})
        total_tags = tags_result.scalar()

        # 统计想法数量
        ideas_query = text(
            "SELECT COUNT(*) FROM ideas WHERE user_id = :user_id AND deleted_at IS NULL"
        )
        ideas_result = await db.execute(ideas_query, {"user_id": current_user.id})
        total_ideas = ideas_result.scalar()

        # 返回统计数据
        return success_response(data={
            "total_papers": total_papers or 0,
            "total_notes": total_notes or 0,
            "total_tags": total_tags or 0,
            "total_ideas": total_ideas or 0,
            "registration_date": current_user.created_at.isoformat() if current_user.created_at else None
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.put("/me", response_model=dict)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息（admin用户只能修改部门、头像等，不能修改账号）"""
    # 更新用户信息
    if user_update.email:
        # 检查邮箱是否已被其他用户使用
        result = await db.execute(
            select(User).where(User.email == user_update.email, User.id != current_user.id)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        current_user.email = user_update.email

    if user_update.department is not None:
        current_user.department = user_update.department

    if user_update.avatar is not None:
        current_user.avatar = user_update.avatar

    await db.commit()
    await db.refresh(current_user)

    user_response = UserResponse.model_validate(current_user)
    return success_response(data=user_response.model_dump(), message="更新成功")


@router.put("/me/password", response_model=dict)
async def update_password(
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    # 防止任何人（包括admin自己）修改admin用户的密码
    if current_user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin用户的密码不可修改"
        )

    # 验证旧密码
    if not verify_password(password_update.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    current_user.password = get_password_hash(password_update.new_password)
    await db.commit()

    return success_response(message="密码修改成功")


@router.get("/", response_model=dict)
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有用户（管理员）"""
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()

    users_response = [UserResponse.model_validate(user).model_dump() for user in users]
    return success_response(data=users_response)


@router.put("/{user_id}/status", response_model=dict)
async def update_user_status(
    user_id: int,
    status_value: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户状态（管理员）"""
    if status_value not in ["pending", "active", "disabled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的状态值"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 防止修改admin用户的信息
    if user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin用户的信息不可修改"
        )

    user.status = status_value
    await db.commit()

    return success_response(message=f"用户状态已更新为: {status_value}")


@router.put("/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户角色（管理员）"""
    if role_update.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的角色值，必须是 user 或 admin"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 防止修改admin用户的角色
    if user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin用户的角色不可修改"
        )

    # 防止管理员修改自己的角色
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的角色"
        )

    user.role = role_update.role
    await db.commit()

    return success_response(message=f"用户角色已更新为: {role_update.role}")


@router.post("/{user_id}/reset-password", response_model=dict)
async def reset_user_password(
    user_id: int,
    password_reset: PasswordResetRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """重置用户密码（管理员）"""
    if len(password_reset.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少为6位"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 防止修改admin用户的密码
    if user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin用户的密码不可修改"
        )

    # 更新密码
    user.password = get_password_hash(password_reset.new_password)
    await db.commit()

    return success_response(message="密码重置成功")


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """删除用户（管理员）- 软删除"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 防止删除admin用户
    if user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin用户不可删除"
        )

    # 防止管理员删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )

    # 软删除：设置状态为disabled
    user.status = "disabled"
    user.updated_at = datetime.utcnow()
    await db.commit()

    return success_response(message="用户已删除")


@router.get("/me/export-data", response_class=JSONResponse)
async def export_user_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出用户的所有个人数据（JSON格式）

    - 需要登录
    - 导出内容：用户信息、论文、笔记、标签、阅读历史
    - 用于数据备份或迁移
    """
    try:
        # 1. 用户基本信息
        user_data = {
            "user_info": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "department": current_user.department,
                "role": current_user.role,
                "status": current_user.status,
                "created_at": current_user.created_at.isoformat(),
                "updated_at": current_user.updated_at.isoformat()
            }
        }

        # 2. 论文数据
        papers_query = select(Paper).where(
            and_(
                Paper.created_by == current_user.id,
                Paper.deleted_at.is_(None)
            )
        )
        papers_result = await db.execute(papers_query)
        papers = papers_result.scalars().all()

        papers_data = []
        for paper in papers:
            paper_dict = {
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "journal": paper.journal,
                "year": paper.year,
                "volume": paper.volume,
                "issue": paper.issue,
                "pages": paper.pages,
                "doi": paper.doi,
                "url": paper.url,
                "abstract": paper.abstract,
                "keywords": paper.keywords,
                "reading_status": paper.reading_status,
                "reading_progress": paper.reading_progress,
                "pdf_path": paper.pdf_path,
                "created_at": paper.created_at.isoformat(),
                "updated_at": paper.updated_at.isoformat()
            }
            papers_data.append(paper_dict)

        user_data["papers"] = papers_data

        # 3. 笔记数据
        notes_query = select(Note).where(
            and_(
                Note.created_by == current_user.id,
                Note.deleted_at.is_(None)
            )
        )
        notes_result = await db.execute(notes_query)
        notes = notes_result.scalars().all()

        notes_data = []
        for note in notes:
            note_dict = {
                "id": note.id,
                "paper_id": note.paper_id,
                "note_type": note.note_type,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat()
            }
            notes_data.append(note_dict)

        user_data["notes"] = notes_data

        # 4. 标签数据
        tags_query = select(Tag).where(Tag.created_by == current_user.id)
        tags_result = await db.execute(tags_query)
        tags = tags_result.scalars().all()

        tags_data = []
        for tag in tags:
            tag_dict = {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "created_at": tag.created_at.isoformat(),
                "updated_at": tag.updated_at.isoformat()
            }
            tags_data.append(tag_dict)

        user_data["tags"] = tags_data

        # 5. 阅读历史数据
        history_query = select(ReadingHistory).where(ReadingHistory.user_id == current_user.id)
        history_result = await db.execute(history_query)
        histories = history_result.scalars().all()

        history_data = []
        for history in histories:
            history_dict = {
                "id": history.id,
                "paper_id": history.paper_id,
                "start_time": history.start_time.isoformat(),
                "end_time": history.end_time.isoformat() if history.end_time else None,
                "duration_seconds": history.duration_seconds,
                "progress_before": history.progress_before,
                "progress_after": history.progress_after,
                "created_at": history.created_at.isoformat()
            }
            history_data.append(history_dict)

        user_data["reading_history"] = history_data

        # 6. 添加导出元数据
        user_data["export_info"] = {
            "export_time": datetime.utcnow().isoformat(),
            "version": "1.0",
            "total_papers": len(papers_data),
            "total_notes": len(notes_data),
            "total_tags": len(tags_data),
            "total_reading_sessions": len(history_data)
        }

        # 返回JSON响应并设置下载文件名
        filename = f"user_{current_user.id}_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        return JSONResponse(
            content=user_data,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出数据失败: {str(e)}"
        )
