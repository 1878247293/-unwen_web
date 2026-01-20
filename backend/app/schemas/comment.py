"""
评论相关的数据验证模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CommentBase(BaseModel):
    """评论基础模型"""
    content: str = Field(..., min_length=1, max_length=5000, description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论ID（用于回复功能）")


class CommentCreate(CommentBase):
    """创建评论时的请求模型"""
    paper_id: int = Field(..., description="论文ID")


class CommentUpdate(BaseModel):
    """更新评论时的请求模型"""
    content: str = Field(..., min_length=1, max_length=5000, description="评论内容")


class CommentUser(BaseModel):
    """评论中的用户信息"""
    id: int
    username: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """评论响应模型"""
    id: int
    paper_id: int
    user_id: int
    content: str
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # 用户信息
    user: CommentUser

    # 回复信息
    replies: List['CommentResponse'] = []
    reply_count: int = 0

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """评论列表响应模型"""
    total: int
    page: int
    page_size: int
    comments: List[CommentResponse]


# 解决循环引用
CommentResponse.model_rebuild()
