"""
论文相关的数据验证模型
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class PaperBase(BaseModel):
    """论文基础模型"""
    title: str = Field(..., min_length=1, max_length=500, description="论文标题")
    authors: Optional[str] = Field(None, max_length=1000, description="作者列表（逗号分隔）")
    journal: Optional[str] = Field(None, max_length=200, description="期刊/会议名称")
    year: Optional[int] = Field(None, ge=1900, le=2100, description="发表年份")
    volume: Optional[str] = Field(None, max_length=50, description="卷号")
    issue: Optional[str] = Field(None, max_length=50, description="期号")
    pages: Optional[str] = Field(None, max_length=50, description="页码范围")
    doi: Optional[str] = Field(None, max_length=200, description="DOI")
    arxiv_id: Optional[str] = Field(None, max_length=100, description="arXiv ID")
    abstract: Optional[str] = Field(None, description="摘要")
    keywords: Optional[str] = Field(None, max_length=500, description="关键词（逗号分隔）")
    url: Optional[str] = Field(None, max_length=500, description="论文链接")
    notes_preview: Optional[str] = Field(None, description="笔记预览")
    reading_status: Optional[str] = Field("unread", description="阅读状态")
    pdf_path: Optional[str] = Field(None, max_length=500, description="PDF文件路径")
    is_shared: Optional[bool] = Field(False, description="是否共享（True=所有用户可见，False=仅创建者和管理员可见）")

    @validator('reading_status')
    def validate_reading_status(cls, v):
        """验证阅读状态"""
        allowed_statuses = ['unread', 'reading', 'read']
        if v not in allowed_statuses:
            raise ValueError(f'reading_status must be one of {allowed_statuses}')
        return v


class PaperCreate(PaperBase):
    """创建论文时的请求模型"""
    pass


class PaperUpdate(BaseModel):
    """更新论文时的请求模型 - 所有字段可选"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    authors: Optional[str] = Field(None, max_length=1000)
    journal: Optional[str] = Field(None, max_length=200)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    volume: Optional[str] = Field(None, max_length=50)
    issue: Optional[str] = Field(None, max_length=50)
    pages: Optional[str] = Field(None, max_length=50)
    doi: Optional[str] = Field(None, max_length=200)
    arxiv_id: Optional[str] = Field(None, max_length=100)
    abstract: Optional[str] = Field(None)
    keywords: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, max_length=500)
    notes_preview: Optional[str] = Field(None)
    reading_status: Optional[str] = Field(None)
    pdf_path: Optional[str] = Field(None, max_length=500)
    is_shared: Optional[bool] = Field(None, description="是否共享")

    @validator('reading_status')
    def validate_reading_status(cls, v):
        """验证阅读状态"""
        if v is not None:
            allowed_statuses = ['unread', 'reading', 'read']
            if v not in allowed_statuses:
                raise ValueError(f'reading_status must be one of {allowed_statuses}')
        return v


class PaperResponse(PaperBase):
    """论文响应模型"""
    id: int
    pdf_path: Optional[str] = None
    is_shared: bool  # 是否共享
    created_by: int
    created_at: datetime
    updated_at: datetime

    # 关联信息
    creator_name: Optional[str] = None  # 创建者用户名
    tags: Optional[List[str]] = []  # 标签列表

    class Config:
        from_attributes = True


class PaperListResponse(BaseModel):
    """论文列表响应模型"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    papers: List[PaperResponse] = Field(..., description="论文列表")


class PaperSearchParams(BaseModel):
    """论文搜索参数"""
    keyword: Optional[str] = Field(None, description="搜索关键词（标题、作者、关键词）")
    year: Optional[int] = Field(None, description="筛选年份")
    author: Optional[str] = Field(None, description="筛选作者")
    reading_status: Optional[str] = Field(None, description="阅读状态")
    created_by: Optional[int] = Field(None, description="创建者ID")
    tag_id: Optional[int] = Field(None, description="标签ID")
    is_shared: Optional[bool] = Field(None, description="是否共享（True=共享论文，False=私人论文，None=全部）")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

    @validator('sort_by')
    def validate_sort_by(cls, v):
        """验证排序字段"""
        allowed_fields = ['created_at', 'updated_at', 'title', 'year']
        if v not in allowed_fields:
            raise ValueError(f'sort_by must be one of {allowed_fields}')
        return v

    @validator('sort_order')
    def validate_sort_order(cls, v):
        """验证排序方向"""
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be asc or desc')
        return v


class PaperFileUploadResponse(BaseModel):
    """文件上传响应"""
    filename: str = Field(..., description="文件名")
    filepath: str = Field(..., description="文件路径")
    size: int = Field(..., description="文件大小（字节）")
