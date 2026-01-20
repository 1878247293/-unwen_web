"""
笔记相关的Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class NoteBase(BaseModel):
    """笔记基础模型"""
    title: Optional[str] = Field(None, max_length=200, description="笔记标题")
    content: str = Field(..., min_length=1, description="笔记内容（Markdown格式）")
    note_type: str = Field("general", max_length=50, description="笔记类型")

    @validator('note_type')
    def validate_note_type(cls, v):
        allowed_types = [
            'general',      # 一般笔记
            'summary',      # 总结
            'method',       # 方法
            'conclusion',   # 结论
            'innovation',   # 创新点
            'limitation',   # 局限性
            'thinking'      # 个人思考
        ]
        if v not in allowed_types:
            raise ValueError(f'笔记类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class NoteCreate(NoteBase):
    """创建笔记"""
    pass


class NoteUpdate(BaseModel):
    """更新笔记"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    note_type: Optional[str] = Field(None, max_length=50)

    @validator('note_type')
    def validate_note_type(cls, v):
        if v is None:
            return v
        allowed_types = [
            'general', 'summary', 'method', 'conclusion',
            'innovation', 'limitation', 'thinking'
        ]
        if v not in allowed_types:
            raise ValueError(f'笔记类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class NoteResponse(NoteBase):
    """笔记响应"""
    id: int
    paper_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """笔记列表响应"""
    total: int
    notes: list[NoteResponse]
