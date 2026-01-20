"""
讨论相关的数据验证模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DiscussionBase(BaseModel):
    """讨论基础模型"""
    content: str = Field(..., min_length=1, max_length=5000, description="讨论内容")
    parent_id: Optional[int] = Field(None, description="父讨论ID（用于回复功能）")


class DiscussionCreate(DiscussionBase):
    """创建讨论时的请求模型"""
    is_anonymous: bool = Field(False, description="是否匿名发布")


class DiscussionUpdate(BaseModel):
    """更新讨论时的请求模型"""
    content: str = Field(..., min_length=1, max_length=5000, description="讨论内容")


class DiscussionUser(BaseModel):
    """讨论中的用户信息"""
    id: Optional[int] = None
    username: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class DiscussionResponse(BaseModel):
    """讨论响应模型"""
    id: int
    user_id: Optional[int] = None
    content: str
    is_anonymous: bool
    is_hidden: bool
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # 用户信息（匿名时为None或显示"匿名用户"）
    user: Optional[DiscussionUser] = None

    # 互动信息
    like_count: int = 0
    is_liked: bool = False
    is_favorited: bool = False

    # 回复信息
    replies: List['DiscussionResponse'] = []
    reply_count: int = 0

    class Config:
        from_attributes = True


class DiscussionListResponse(BaseModel):
    """讨论列表响应模型"""
    total: int
    page: int
    page_size: int
    discussions: List[DiscussionResponse]


class ReportCreate(BaseModel):
    """举报创建请求模型"""
    reason: str = Field(..., min_length=1, max_length=1000, description="举报原因")


class ReportResponse(BaseModel):
    """举报响应模型"""
    id: int
    discussion_id: int
    user_id: int
    reason: str
    status: str
    created_at: datetime
    handled_at: Optional[datetime] = None
    handled_by: Optional[int] = None

    # 举报人信息
    reporter: Optional[DiscussionUser] = None
    # 处理人信息
    handler: Optional[DiscussionUser] = None

    class Config:
        from_attributes = True


class ReportHandleRequest(BaseModel):
    """处理举报请求模型"""
    status: str = Field(..., description="处理状态：handled（已处理）或 rejected（已驳回）")


class SystemSettingUpdate(BaseModel):
    """系统设置更新模型"""
    setting_value: str = Field(..., description="设置值")


# 解决循环引用
DiscussionResponse.model_rebuild()
