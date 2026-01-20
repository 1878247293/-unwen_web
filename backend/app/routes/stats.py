"""
统计相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import Dict, Any
from datetime import datetime, timedelta

from app.models import get_db
from app.models.database import User, Paper, Note, Tag
from app.utils.dependencies import get_current_user, get_current_admin_user
from app.utils.response import success_response

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/dashboard", response_model=dict)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取Dashboard统计数据

    返回：
    - 论文总数
    - 笔记总数
    - 标签总数
    - 按阅读状态分组的论文数
    - 最近阅读的论文列表
    """
    try:
        # 1. 论文总数（未删除）
        paper_count_query = select(func.count(Paper.id)).where(
            and_(
                Paper.created_by == current_user.id,
                Paper.deleted_at.is_(None)
            )
        )
        paper_count_result = await db.execute(paper_count_query)
        total_papers = paper_count_result.scalar() or 0

        # 2. 笔记总数（未删除）
        note_count_query = select(func.count(Note.id)).where(
            and_(
                Note.created_by == current_user.id,
                Note.deleted_at.is_(None)
            )
        )
        note_count_result = await db.execute(note_count_query)
        total_notes = note_count_result.scalar() or 0

        # 3. 标签总数
        tag_count_query = select(func.count(Tag.id)).where(
            Tag.created_by == current_user.id
        )
        tag_count_result = await db.execute(tag_count_query)
        total_tags = tag_count_result.scalar() or 0

        # 4. 按阅读状态分组的论文数
        reading_status_query = select(
            Paper.reading_status,
            func.count(Paper.id).label('count')
        ).where(
            and_(
                Paper.created_by == current_user.id,
                Paper.deleted_at.is_(None)
            )
        ).group_by(Paper.reading_status)

        reading_status_result = await db.execute(reading_status_query)
        reading_status_rows = reading_status_result.all()

        reading_stats = {
            'unread': 0,
            'reading': 0,
            'read': 0
        }
        for row in reading_status_rows:
            reading_stats[row[0]] = row[1]

        # 5. 最近更新的论文（最近阅读）
        # 使用 updated_at 作为"最近阅读"的指标
        recent_papers_query = select(Paper).where(
            and_(
                Paper.created_by == current_user.id,
                Paper.deleted_at.is_(None)
            )
        ).order_by(desc(Paper.updated_at)).limit(5)

        recent_papers_result = await db.execute(recent_papers_query)
        recent_papers = recent_papers_result.scalars().all()

        # 构造最近论文数据
        recent_papers_list = []
        for paper in recent_papers:
            recent_papers_list.append({
                'id': paper.id,
                'title': paper.title,
                'authors': paper.authors,
                'journal': paper.journal,
                'year': paper.year,
                'reading_status': paper.reading_status,
                'updated_at': paper.updated_at
            })

        # 返回统计数据
        return success_response(data={
            'total_papers': total_papers,
            'total_notes': total_notes,
            'total_tags': total_tags,
            'reading_stats': reading_stats,
            'recent_papers': recent_papers_list
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )


@router.get("/reading-progress", response_model=dict)
async def get_reading_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取阅读进度统计

    返回：
    - 总论文数
    - 已读论文数
    - 在读论文数
    - 未读论文数
    - 阅读完成百分比
    """
    try:
        # 获取各状态论文数
        status_query = select(
            Paper.reading_status,
            func.count(Paper.id).label('count')
        ).where(
            and_(
                Paper.created_by == current_user.id,
                Paper.deleted_at.is_(None)
            )
        ).group_by(Paper.reading_status)

        status_result = await db.execute(status_query)
        status_rows = status_result.all()

        stats = {
            'unread': 0,
            'reading': 0,
            'read': 0
        }

        for row in status_rows:
            stats[row[0]] = row[1]

        total = stats['unread'] + stats['reading'] + stats['read']
        percentage = round((stats['read'] / total * 100) if total > 0 else 0, 1)

        return success_response(data={
            'total': total,
            'unread': stats['unread'],
            'reading': stats['reading'],
            'read': stats['read'],
            'percentage': percentage
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取阅读进度失败: {str(e)}"
        )


@router.get("/admin/overview", response_model=dict)
async def get_admin_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取管理员统计概览（全站数据）

    返回：
    - 用户总数（按状态分组）
    - 论文总数
    - 笔记总数
    - 标签总数
    - 最近7天新增用户
    - 最近7天新增论文
    """
    try:
        # 1. 用户统计
        # 总用户数
        total_users_query = select(func.count(User.id))
        total_users_result = await db.execute(total_users_query)
        total_users = total_users_result.scalar() or 0

        # 按状态分组
        user_status_query = select(
            User.status,
            func.count(User.id).label('count')
        ).group_by(User.status)
        user_status_result = await db.execute(user_status_query)
        user_status_rows = user_status_result.all()

        user_stats = {
            'total': total_users,
            'active': 0,
            'pending': 0,
            'disabled': 0
        }
        for row in user_status_rows:
            user_stats[row[0]] = row[1]

        # 按角色分组
        user_role_query = select(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role)
        user_role_result = await db.execute(user_role_query)
        user_role_rows = user_role_result.all()

        user_role_stats = {'admin': 0, 'user': 0}
        for row in user_role_rows:
            user_role_stats[row[0]] = row[1]

        # 2. 论文总数（未删除）
        total_papers_query = select(func.count(Paper.id)).where(
            Paper.deleted_at.is_(None)
        )
        total_papers_result = await db.execute(total_papers_query)
        total_papers = total_papers_result.scalar() or 0

        # 按阅读状态分组
        paper_status_query = select(
            Paper.reading_status,
            func.count(Paper.id).label('count')
        ).where(
            Paper.deleted_at.is_(None)
        ).group_by(Paper.reading_status)
        paper_status_result = await db.execute(paper_status_query)
        paper_status_rows = paper_status_result.all()

        paper_stats = {
            'total': total_papers,
            'unread': 0,
            'reading': 0,
            'read': 0
        }
        for row in paper_status_rows:
            paper_stats[row[0]] = row[1]

        # 3. 笔记总数（未删除）
        total_notes_query = select(func.count(Note.id)).where(
            Note.deleted_at.is_(None)
        )
        total_notes_result = await db.execute(total_notes_query)
        total_notes = total_notes_result.scalar() or 0

        # 4. 标签总数
        total_tags_query = select(func.count(Tag.id))
        total_tags_result = await db.execute(total_tags_query)
        total_tags = total_tags_result.scalar() or 0

        # 5. 最近7天新增用户
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        new_users_query = select(func.count(User.id)).where(
            User.created_at >= seven_days_ago
        )
        new_users_result = await db.execute(new_users_query)
        new_users = new_users_result.scalar() or 0

        # 6. 最近7天新增论文
        new_papers_query = select(func.count(Paper.id)).where(
            and_(
                Paper.created_at >= seven_days_ago,
                Paper.deleted_at.is_(None)
            )
        )
        new_papers_result = await db.execute(new_papers_query)
        new_papers = new_papers_result.scalar() or 0

        # 7. 最近7天新增笔记
        new_notes_query = select(func.count(Note.id)).where(
            and_(
                Note.created_at >= seven_days_ago,
                Note.deleted_at.is_(None)
            )
        )
        new_notes_result = await db.execute(new_notes_query)
        new_notes = new_notes_result.scalar() or 0

        return success_response(data={
            'user_stats': user_stats,
            'user_role_stats': user_role_stats,
            'paper_stats': paper_stats,
            'total_notes': total_notes,
            'total_tags': total_tags,
            'recent_activity': {
                'new_users_7d': new_users,
                'new_papers_7d': new_papers,
                'new_notes_7d': new_notes
            }
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取管理员统计失败: {str(e)}"
        )


@router.get("/admin/user-growth", response_model=dict)
async def get_user_growth(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取用户增长趋势（最近N天）

    参数：
    - days: 统计天数，默认30天
    """
    try:
        # 获取最近N天每天的新增用户数
        start_date = datetime.utcnow() - timedelta(days=days)

        # 按天分组统计
        growth_query = select(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).where(
            User.created_at >= start_date
        ).group_by(
            func.date(User.created_at)
        ).order_by(
            func.date(User.created_at)
        )

        growth_result = await db.execute(growth_query)
        growth_rows = growth_result.all()

        # 构造结果
        growth_data = []
        for row in growth_rows:
            growth_data.append({
                'date': str(row[0]),
                'count': row[1]
            })

        return success_response(data={
            'days': days,
            'growth': growth_data
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户增长趋势失败: {str(e)}"
        )
