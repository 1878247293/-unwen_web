"""
标签相关的数据验证模型
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    color: str = Field("#1890ff", max_length=20, description="标签颜色（Hex格式）")

    @validator('color')
    def validate_color(cls, v):
        """验证颜色格式"""
        if not v.startswith('#'):
            raise ValueError('color must start with #')
        if len(v) not in [4, 7]:  # #fff 或 #ffffff
            raise ValueError('color must be in format #RGB or #RRGGBB')
        return v


class TagCreate(TagBase):
    """创建标签时的请求模型"""
    pass


class TagUpdate(BaseModel):
    """更新标签时的请求模型 - 所有字段可选"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, max_length=20)

    @validator('color')
    def validate_color(cls, v):
        """验证颜色格式"""
        if v is not None:
            if not v.startswith('#'):
                raise ValueError('color must start with #')
            if len(v) not in [4, 7]:
                raise ValueError('color must be in format #RGB or #RRGGBB')
        return v


class TagResponse(TagBase):
    """标签响应模型"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    # 关联信息
    paper_count: Optional[int] = 0  # 关联的论文数量

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """标签列表响应模型"""
    total: int = Field(..., description="总数")
    tags: List[TagResponse] = Field(..., description="标签列表")


class PaperTagCreate(BaseModel):
    """为论文添加标签的请求模型"""
    tag_ids: List[int] = Field(..., min_items=1, description="标签ID列表")
