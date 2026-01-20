"""
阅读进度和历史相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import List
from datetime import datetime, timedelta

from app.models import get_db
from app.models.database import Paper, ReadingHistory, User
from app.schemas.reading import (
    ReadingProgressUpdate,
    ReadingSessionCreate,
    ReadingHistoryResponse,
    ReadingStatsResponse,
    PaperReadingStats
)
from app.utils.dependencies import get_current_user
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/reading", tags=["reading"])


@router.put("/papers/{paper_id}/progress", response_model=dict)
async def update_reading_progress(
    paper_id: int,
    progress_data: ReadingProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新论文阅读进度

    - 需要登录
    - 只能更新自己的论文
    - 自动更新reading_status
    """
    try:
        # 查询论文
        query = select(Paper).where(
            and_(
                Paper.id == paper_id,
                Paper.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        paper = result.scalar_one_or_none()

        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文不存在"
            )

        # 权限检查
        if paper.created_by != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此论文"
            )

        # 更新阅读进度
        paper.reading_progress = progress_data.reading_progress

        # 自动更新阅读状态
        if progress_data.reading_progress == 0:
            paper.reading_status = "unread"
        elif progress_data.reading_progress == 100:
            paper.reading_status = "read"
        else:
            paper.reading_status = "reading"

        paper.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(paper)

        return success_response(
            data={
                "id": paper.id,
                "reading_progress": paper.reading_progress,
                "reading_status": paper.reading_status
            },
            message="阅读进度更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新阅读进度失败: {str(e)}"
        )


@router.post("/papers/{paper_id}/sessions", response_model=dict)
async def create_reading_session(
    paper_id: int,
    session_data: ReadingSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    记录阅读会话

    - 需要登录
    - 记录阅读开始时间、结束时间、时长
    - 记录阅读前后进度
    """
    try:
        # 验证论文存在
        query = select(Paper).where(
            and_(
                Paper.id == paper_id,
                Paper.deleted_at.is_(None)
            )
        )
        result = await db.execute(query)
        paper = result.scalar_one_or_none()

        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文不存在"
            )

        # 创建阅读历史记录
        reading_history = ReadingHistory(
            paper_id=paper_id,
            user_id=current_user.id,
            start_time=session_data.start_time,
            end_time=session_data.end_time,
            duration_seconds=session_data.duration_seconds,
            progress_before=session_data.progress_before,
            progress_after=session_data.progress_after
        )

        db.add(reading_history)
        await db.commit()
        await db.refresh(reading_history)

        return success_response(
            data={
                "id": reading_history.id,
                "paper_id": reading_history.paper_id,
                "duration_seconds": reading_history.duration_seconds,
                "progress_before": reading_history.progress_before,
                "progress_after": reading_history.progress_after
            },
            message="阅读记录创建成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建阅读记录失败: {str(e)}"
        )


@router.get("/papers/{paper_id}/history", response_model=dict)
async def get_paper_reading_history(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取论文的阅读历史

    - 需要登录
    - 返回该论文的所有阅读记录
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

        if paper.created_by != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此论文"
            )

        # 查询阅读历史
        query = select(ReadingHistory).where(
            and_(
                ReadingHistory.paper_id == paper_id,
                ReadingHistory.user_id == current_user.id
            )
        ).order_by(desc(ReadingHistory.start_time))

        result = await db.execute(query)
        histories = result.scalars().all()

        # 构建响应数据
        history_list = [
            {
                "id": h.id,
                "paper_id": h.paper_id,
                "user_id": h.user_id,
                "start_time": h.start_time,
                "end_time": h.end_time,
                "duration_seconds": h.duration_seconds,
                "progress_before": h.progress_before,
                "progress_after": h.progress_after,
                "created_at": h.created_at
            }
            for h in histories
        ]

        # 计算统计信息
        total_time = sum(h.duration_seconds for h in histories)
        total_sessions = len(histories)

        return success_response(
            data={
                "paper_id": paper_id,
                "paper_title": paper.title,
                "current_progress": paper.reading_progress,
                "total_reading_time": total_time,
                "total_sessions": total_sessions,
                "history": history_list
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取阅读历史失败: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_reading_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户阅读统计

    - 需要登录
    - 返回总阅读时间、阅读次数、平均时长等
    """
    try:
        # 查询用户所有阅读历史
        query = select(ReadingHistory).where(
            ReadingHistory.user_id == current_user.id
        )
        result = await db.execute(query)
        histories = result.scalars().all()

        # 计算统计数据
        total_time = sum(h.duration_seconds for h in histories)
        total_sessions = len(histories)
        avg_duration = total_time / total_sessions if total_sessions > 0 else 0

        # 查询论文统计
        papers_query = select(Paper).where(
            and_(
                Paper.created_by == current_user.id,
                Paper.deleted_at.is_(None)
            )
        )
        papers_result = await db.execute(papers_query)
        papers = papers_result.scalars().all()

        papers_read = sum(1 for p in papers if p.reading_status == "read")
        papers_in_progress = sum(1 for p in papers if p.reading_status == "reading")

        # 最近10次阅读记录
        recent_query = select(ReadingHistory).where(
            ReadingHistory.user_id == current_user.id
        ).order_by(desc(ReadingHistory.start_time)).limit(10)

        recent_result = await db.execute(recent_query)
        recent_histories = recent_result.scalars().all()

        # 获取相关论文信息
        paper_ids = [h.paper_id for h in recent_histories]
        if paper_ids:
            papers_query = select(Paper).where(Paper.id.in_(paper_ids))
            papers_result = await db.execute(papers_query)
            paper_dict = {p.id: p for p in papers_result.scalars().all()}
        else:
            paper_dict = {}

        recent_sessions = [
            {
                "id": h.id,
                "paper_id": h.paper_id,
                "paper_title": paper_dict.get(h.paper_id).title if h.paper_id in paper_dict else "未知",
                "start_time": h.start_time,
                "duration_seconds": h.duration_seconds,
                "progress_after": h.progress_after
            }
            for h in recent_histories
            if h.paper_id in paper_dict
        ]

        return success_response(
            data={
                "total_reading_time": total_time,
                "total_sessions": total_sessions,
                "average_session_duration": round(avg_duration, 2),
                "papers_read": papers_read,
                "papers_in_progress": papers_in_progress,
                "recent_sessions": recent_sessions
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取阅读统计失败: {str(e)}"
        )


@router.get("/papers/stats", response_model=dict)
async def get_papers_reading_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有论文的阅读统计

    - 需要登录
    - 返回每篇论文的阅读时间、次数、进度等
    """
    try:
        # 查询用户的所有论文
        papers_query = select(Paper).where(
            and_(
                Paper.created_by == current_user.id,
                Paper.deleted_at.is_(None)
            )
        )
        papers_result = await db.execute(papers_query)
        papers = papers_result.scalars().all()

        paper_stats = []

        for paper in papers:
            # 查询该论文的阅读历史
            history_query = select(ReadingHistory).where(
                and_(
                    ReadingHistory.paper_id == paper.id,
                    ReadingHistory.user_id == current_user.id
                )
            ).order_by(desc(ReadingHistory.start_time))

            history_result = await db.execute(history_query)
            histories = history_result.scalars().all()

            total_time = sum(h.duration_seconds for h in histories)
            session_count = len(histories)
            last_read = histories[0].start_time if histories else None

            paper_stats.append({
                "paper_id": paper.id,
                "paper_title": paper.title,
                "total_reading_time": total_time,
                "session_count": session_count,
                "current_progress": paper.reading_progress,
                "reading_status": paper.reading_status,
                "last_read_at": last_read
            })

        # 按最后阅读时间排序
        paper_stats.sort(key=lambda x: x['last_read_at'] or datetime.min, reverse=True)

        return success_response(data={"papers": paper_stats})

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取论文阅读统计失败: {str(e)}"
        )
