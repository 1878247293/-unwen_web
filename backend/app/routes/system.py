"""
系统资源监控相关的API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
import psutil
import os
import shutil
from datetime import datetime

from app.models import get_db
from app.models.database import User, Paper, Note, Tag, Comment, Discussion
from app.utils.dependencies import get_current_admin_user
from app.utils.response import success_response, error_response
from sqlalchemy import text

router = APIRouter(prefix="/system", tags=["系统监控"])


def get_size_format(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_directory_size(path: str) -> int:
    """计算目录大小（字节）"""
    total = 0
    try:
        if os.path.exists(path):
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += get_directory_size(entry.path)
    except Exception as e:
        print(f"Error calculating directory size for {path}: {e}")
    return total


@router.get("/resources", response_model=dict)
async def get_system_resources(
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取系统资源使用情况（管理员）

    返回CPU、内存、磁盘使用率等信息
    """
    try:
        # CPU使用率（过去1秒的平均值）
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024 ** 3)
        memory_total_gb = memory.total / (1024 ** 3)
        memory_percent = memory.percent

        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)
        disk_percent = disk.percent

        # 系统启动时间
        boot_time = datetime.fromtimestamp(psutil.boot_time())

        return success_response(
            data={
                "cpu": {
                    "percent": round(cpu_percent, 2),
                    "count": cpu_count
                },
                "memory": {
                    "used_gb": round(memory_used_gb, 2),
                    "total_gb": round(memory_total_gb, 2),
                    "percent": round(memory_percent, 2)
                },
                "disk": {
                    "used_gb": round(disk_used_gb, 2),
                    "total_gb": round(disk_total_gb, 2),
                    "percent": round(disk_percent, 2)
                },
                "boot_time": boot_time.isoformat(),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统资源信息失败: {str(e)}"
        )


@router.get("/statistics", response_model=dict)
async def get_system_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取系统统计信息（管理员）

    返回用户数、论文数、讨论数等统计数据
    """
    try:
        # 用户统计
        total_users_query = select(func.count(User.id))
        total_users_result = await db.execute(total_users_query)
        total_users = total_users_result.scalar()

        active_users_query = select(func.count(User.id)).where(User.status == "active")
        active_users_result = await db.execute(active_users_query)
        active_users = active_users_result.scalar()

        # 论文统计
        total_papers_query = select(func.count(Paper.id)).where(Paper.deleted_at.is_(None))
        total_papers_result = await db.execute(total_papers_query)
        total_papers = total_papers_result.scalar()

        # 笔记统计
        total_notes_query = select(func.count(Note.id)).where(Note.deleted_at.is_(None))
        total_notes_result = await db.execute(total_notes_query)
        total_notes = total_notes_result.scalar()

        # 标签统计
        total_tags_query = select(func.count(Tag.id))
        total_tags_result = await db.execute(total_tags_query)
        total_tags = total_tags_result.scalar()

        # 评论统计
        total_comments_query = select(func.count(Comment.id)).where(Comment.deleted_at.is_(None))
        total_comments_result = await db.execute(total_comments_query)
        total_comments = total_comments_result.scalar()

        # 讨论统计
        total_discussions_query = select(func.count(Discussion.id)).where(Discussion.deleted_at.is_(None))
        total_discussions_result = await db.execute(total_discussions_query)
        total_discussions = total_discussions_result.scalar()

        # 想法统计（使用原始SQL）
        total_ideas_result = await db.execute(text("SELECT COUNT(*) FROM ideas WHERE deleted_at IS NULL"))
        total_ideas = total_ideas_result.scalar() or 0

        # 网站收藏统计（使用原始SQL）
        total_websites_result = await db.execute(text("SELECT COUNT(*) FROM websites WHERE deleted_at IS NULL"))
        total_websites = total_websites_result.scalar() or 0

        # 建议统计（使用原始SQL）
        total_suggestions_result = await db.execute(text("SELECT COUNT(*) FROM suggestions"))
        total_suggestions = total_suggestions_result.scalar() or 0

        pending_suggestions_result = await db.execute(text("SELECT COUNT(*) FROM suggestions WHERE status = 'pending'"))
        pending_suggestions = pending_suggestions_result.scalar() or 0

        # 通知统计（使用原始SQL）
        total_notifications_result = await db.execute(text("SELECT COUNT(*) FROM notifications"))
        total_notifications = total_notifications_result.scalar() or 0

        return success_response(
            data={
                "users": {
                    "total": total_users or 0,
                    "active": active_users or 0,
                    "pending": (total_users or 0) - (active_users or 0)
                },
                "papers": {
                    "total": total_papers or 0
                },
                "notes": {
                    "total": total_notes or 0
                },
                "tags": {
                    "total": total_tags or 0
                },
                "comments": {
                    "total": total_comments or 0
                },
                "discussions": {
                    "total": total_discussions or 0
                },
                "ideas": {
                    "total": total_ideas or 0
                },
                "websites": {
                    "total": total_websites or 0
                },
                "suggestions": {
                    "total": total_suggestions or 0,
                    "pending": pending_suggestions or 0
                },
                "notifications": {
                    "total": total_notifications or 0
                }
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/storage", response_model=dict)
async def get_storage_info(
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取存储使用情况（管理员）

    返回上传文件占用的磁盘空间
    """
    try:
        # 计算各个目录的大小
        papers_size = get_directory_size("data/uploads/papers")
        pdfs_size = get_directory_size("data/uploads/pdfs")
        avatars_size = get_directory_size("data/uploads/avatars")
        database_size = os.path.getsize("data/database.db") if os.path.exists("data/database.db") else 0

        total_uploads = papers_size + pdfs_size + avatars_size
        total_size = total_uploads + database_size

        return success_response(
            data={
                "uploads": {
                    "papers": {
                        "size_bytes": papers_size,
                        "size_formatted": get_size_format(papers_size)
                    },
                    "pdfs": {
                        "size_bytes": pdfs_size,
                        "size_formatted": get_size_format(pdfs_size)
                    },
                    "avatars": {
                        "size_bytes": avatars_size,
                        "size_formatted": get_size_format(avatars_size)
                    },
                    "total": {
                        "size_bytes": total_uploads,
                        "size_formatted": get_size_format(total_uploads)
                    }
                },
                "database": {
                    "size_bytes": database_size,
                    "size_formatted": get_size_format(database_size)
                },
                "total": {
                    "size_bytes": total_size,
                    "size_formatted": get_size_format(total_size)
                }
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取存储信息失败: {str(e)}"
        )


@router.get("/health", response_model=dict)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取系统健康状态（管理员）

    综合检查系统各项指标是否健康
    """
    try:
        health_status = {
            "overall": "healthy",
            "issues": []
        }

        # 检查CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            health_status["issues"].append("CPU使用率过高")
            health_status["overall"] = "warning"

        # 检查内存使用率
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 90:
            health_status["issues"].append("内存使用率过高")
            health_status["overall"] = "warning"

        # 检查磁盘使用率
        disk_percent = psutil.disk_usage('/').percent
        if disk_percent > 90:
            health_status["issues"].append("磁盘使用率过高")
            health_status["overall"] = "critical"
        elif disk_percent > 80:
            health_status["issues"].append("磁盘空间不足")
            if health_status["overall"] == "healthy":
                health_status["overall"] = "warning"

        # 检查数据库连接
        try:
            await db.execute(select(1))
            health_status["database"] = "connected"
        except Exception:
            health_status["issues"].append("数据库连接异常")
            health_status["overall"] = "critical"
            health_status["database"] = "disconnected"

        return success_response(data=health_status)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统健康状态失败: {str(e)}"
        )
