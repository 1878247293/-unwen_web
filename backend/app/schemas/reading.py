"""
阅读进度和历史相关的Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class ReadingProgressUpdate(BaseModel):
    """更新阅读进度"""
    reading_progress: int = Field(..., ge=0, le=100, description="阅读进度百分比")

    @validator('reading_progress')
    def validate_progress(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('阅读进度必须在0-100之间')
        return v


class ReadingSessionCreate(BaseModel):
    """创建阅读会话"""
    start_time: datetime = Field(..., description="开始阅读时间")
    end_time: Optional[datetime] = Field(None, description="结束阅读时间")
    duration_seconds: int = Field(0, ge=0, description="阅读时长（秒）")
    progress_before: int = Field(0, ge=0, le=100, description="阅读前进度")
    progress_after: int = Field(0, ge=0, le=100, description="阅读后进度")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values and v < values['start_time']:
            raise ValueError('结束时间不能早于开始时间')
        return v

    @validator('duration_seconds')
    def validate_duration(cls, v, values):
        if v < 0:
            raise ValueError('阅读时长不能为负数')
        # 如果提供了开始和结束时间，验证时长
        if 'start_time' in values and 'end_time' in values and values['end_time']:
            calculated_duration = int((values['end_time'] - values['start_time']).total_seconds())
            if abs(calculated_duration - v) > 60:  # 允许60秒误差
                raise ValueError(f'阅读时长与时间差不匹配')
        return v


class ReadingHistoryResponse(BaseModel):
    """阅读历史响应"""
    id: int
    paper_id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: int
    progress_before: int
    progress_after: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReadingStatsResponse(BaseModel):
    """阅读统计响应"""
    total_reading_time: int = Field(..., description="总阅读时间（秒）")
    total_sessions: int = Field(..., description="总阅读次数")
    average_session_duration: float = Field(..., description="平均每次阅读时长（秒）")
    papers_read: int = Field(..., description="已读论文数")
    papers_in_progress: int = Field(..., description="在读论文数")
    recent_sessions: list = Field(default=[], description="最近阅读记录")


class PaperReadingStats(BaseModel):
    """单篇论文阅读统计"""
    paper_id: int
    paper_title: str
    total_reading_time: int = Field(..., description="总阅读时间（秒）")
    session_count: int = Field(..., description="阅读次数")
    current_progress: int = Field(..., description="当前阅读进度")
    reading_status: str = Field(..., description="阅读状态")
    last_read_at: Optional[datetime] = Field(None, description="最后阅读时间")
