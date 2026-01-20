"""
论文管理相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from typing import List, Optional
import os
import shutil
import re
from datetime import datetime

from app.models import get_db
from app.models.database import Paper, User, Tag, PaperTag
from app.schemas.paper import (
    PaperCreate,
    PaperUpdate,
    PaperResponse,
    PaperListResponse,
    PaperSearchParams,
    PaperFileUploadResponse,
)
from app.utils.dependencies import get_current_user, check_permission
from app.utils.response import success_response, error_response
from app.config import settings

router = APIRouter(prefix="/papers", tags=["papers"])


# 文件上传配置
UPLOAD_DIR = "data/uploads/papers"
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def ensure_upload_dir():
    """确保上传目录存在"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


async def load_paper_tags(paper_id: int, db: AsyncSession) -> list:
    """加载论文的标签列表"""
    query = select(Tag).join(
        PaperTag, Tag.id == PaperTag.tag_id
    ).where(
        PaperTag.paper_id == paper_id
    )

    result = await db.execute(query)
    tags = result.scalars().all()

    return [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in tags]


def validate_file(file: UploadFile) -> None:
    """验证上传的文件"""
    # 检查文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )


@router.post("/upload", response_model=dict)
async def upload_paper_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传论文PDF文件

    - 仅支持PDF格式
    - 文件大小限制：50MB
    - 返回文件路径用于创建论文记录
    """
    try:
        # 验证文件
        validate_file(file)

        # 确保上传目录存在
        ensure_upload_dir()

        # 生成唯一文件名（使用时间戳 + 用户ID）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(file.filename)[1].lower()
        safe_filename = f"{current_user.id}_{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 获取文件大小
        file_size = os.path.getsize(file_path)

        # 检查文件大小
        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件太大，最大支持 {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        return success_response(
            data={
                "filename": safe_filename,
                "filepath": file_path,
                "size": file_size
            },
            message="文件上传成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.post("/", response_model=dict)
async def create_paper(
    paper_data: PaperCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新论文记录

    - 需要登录
    - 自动关联到当前用户
    - 可选上传PDF文件路径
    """
    try:
        # 创建论文记录
        new_paper = Paper(
            **paper_data.model_dump(),
            created_by=current_user.id
        )

        db.add(new_paper)
        await db.commit()
        await db.refresh(new_paper)

        # 手动构造响应数据（避免访问异步关系）
        paper_dict = {
            "id": new_paper.id,
            "title": new_paper.title,
            "authors": new_paper.authors,
            "journal": new_paper.journal,
            "year": new_paper.year,
            "volume": new_paper.volume,
            "issue": new_paper.issue,
            "pages": new_paper.pages,
            "doi": new_paper.doi,
            "arxiv_id": new_paper.arxiv_id,
            "abstract": new_paper.abstract,
            "keywords": new_paper.keywords,
            "url": new_paper.url,
            "notes_preview": new_paper.notes_preview,
            "reading_status": new_paper.reading_status,
            "reading_progress": new_paper.reading_progress,
            "pdf_path": new_paper.pdf_path,
            "is_shared": new_paper.is_shared,
            "created_by": new_paper.created_by,
            "created_at": new_paper.created_at,
            "updated_at": new_paper.updated_at,
            "creator_name": current_user.username,
            "tags": []  # 新创建的论文没有标签
        }

        return success_response(
            data=paper_dict,
            message="论文添加成功"
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建论文失败: {str(e)}"
        )


@router.get("/", response_model=dict)
async def get_papers(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    year: Optional[int] = Query(None, description="筛选年份"),
    author: Optional[str] = Query(None, description="筛选作者"),
    reading_status: Optional[str] = Query(None, description="阅读状态"),
    tag_id: Optional[int] = Query(None, description="标签ID"),
    created_by: Optional[int] = Query(None, description="创建者ID"),
    is_shared: Optional[bool] = Query(None, description="是否共享（True=共享论文，False=私人论文，None=全部）"),
    only_my_papers: Optional[bool] = Query(None, description="只看我的论文（True=只看自己创建的，False/None=全部）"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取论文列表

    - 支持搜索和筛选
    - 支持分页
    - 普通用户可以看到：自己创建的论文 + 所有共享论文
    - 管理员可以看所有论文
    """
    try:
        # 构建基础查询（未删除的论文）
        query = select(Paper).where(Paper.deleted_at.is_(None))

        # 权限过滤
        if current_user.role != "admin":
            # 普通用户：只能看自己的论文或共享论文
            query = query.where(
                or_(
                    Paper.created_by == current_user.id,  # 自己创建的
                    Paper.is_shared == True  # 或者是共享的
                )
            )

        # only_my_papers 筛选（只看我的论文）
        if only_my_papers:
            query = query.where(Paper.created_by == current_user.id)
        # is_shared 筛选（用户可以选择只看共享或只看私人）
        elif is_shared is not None:
            query = query.where(Paper.is_shared == is_shared)

        # 标签筛选
        if tag_id:
            query = query.join(
                PaperTag, Paper.id == PaperTag.paper_id
            ).where(
                PaperTag.tag_id == tag_id
            )

        # 关键词搜索（标题、作者、关键词、摘要）
        if keyword:
            search_filter = or_(
                Paper.title.ilike(f"%{keyword}%"),
                Paper.authors.ilike(f"%{keyword}%"),
                Paper.keywords.ilike(f"%{keyword}%"),
                Paper.abstract.ilike(f"%{keyword}%")
            )
            query = query.where(search_filter)

        # 年份筛选
        if year:
            query = query.where(Paper.year == year)

        # 作者筛选
        if author:
            query = query.where(Paper.authors.ilike(f"%{author}%"))

        # 阅读状态筛选
        if reading_status:
            query = query.where(Paper.reading_status == reading_status)

        # 创建者筛选（管理员可用）
        if created_by and current_user.role == "admin":
            query = query.where(Paper.created_by == created_by)

        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 排序
        order_column = getattr(Paper, sort_by, Paper.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # 执行查询
        result = await db.execute(query)
        papers = result.scalars().all()

        # 获取创建者信息
        user_ids = list(set(paper.created_by for paper in papers))
        users = {}
        if user_ids:  # 只有当有论文时才查询用户
            users_query = select(User).where(User.id.in_(user_ids))
            users_result = await db.execute(users_query)
            users = {user.id: user.username for user in users_result.scalars().all()}

        # 构造响应数据（手动构建，避免访问异步关系）
        paper_list = []
        for paper in papers:
            # 加载论文的标签
            tags = await load_paper_tags(paper.id, db)

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
                "arxiv_id": paper.arxiv_id,
                "abstract": paper.abstract,
                "keywords": paper.keywords,
                "url": paper.url,
                "notes_preview": paper.notes_preview,
                "reading_status": paper.reading_status,
                "reading_progress": paper.reading_progress,
                "pdf_path": paper.pdf_path,
                "is_shared": paper.is_shared,
                "created_by": paper.created_by,
                "created_at": paper.created_at,
                "updated_at": paper.updated_at,
                "creator_name": users.get(paper.created_by),
                "tags": tags
            }
            paper_list.append(paper_dict)

        return success_response(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "papers": paper_list
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取论文列表失败: {str(e)}"
        )


@router.get("/{paper_id}", response_model=dict)
async def get_paper(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个论文详情

    - 需要登录
    - 普通用户可以查看：自己的论文 + 共享论文
    - 管理员可以查看所有论文
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
        # 管理员可以看所有论文，普通用户可以看自己的或共享的论文
        if current_user.role != "admin":
            if paper.created_by != current_user.id and not paper.is_shared:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问此论文"
                )

        # 获取创建者信息
        user_query = select(User).where(User.id == paper.created_by)
        user_result = await db.execute(user_query)
        creator = user_result.scalar_one_or_none()

        # 加载论文的标签
        tags = await load_paper_tags(paper.id, db)

        # 构造响应数据（手动构建，避免访问异步关系）
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
            "arxiv_id": paper.arxiv_id,
            "abstract": paper.abstract,
            "keywords": paper.keywords,
            "url": paper.url,
            "notes_preview": paper.notes_preview,
            "reading_status": paper.reading_status,
            "reading_progress": paper.reading_progress,
            "pdf_path": paper.pdf_path,
            "is_shared": paper.is_shared,
            "created_by": paper.created_by,
            "created_at": paper.created_at,
            "updated_at": paper.updated_at,
            "creator_name": creator.username if creator else None,
            "tags": tags
        }

        return success_response(data=paper_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取论文详情失败: {str(e)}"
        )


@router.put("/{paper_id}", response_model=dict)
async def update_paper(
    paper_id: int,
    paper_data: PaperUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新论文信息

    - 需要登录
    - 只能更新自己创建的论文（管理员可以更新所有论文）
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
        if not check_permission(current_user, paper.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此论文"
            )

        # 更新字段（只更新提供的字段）
        update_data = paper_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(paper, field, value)

        paper.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(paper)

        # 加载论文的标签
        tags = await load_paper_tags(paper.id, db)

        # 构造响应数据（手动构建，避免访问异步关系）
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
            "arxiv_id": paper.arxiv_id,
            "abstract": paper.abstract,
            "keywords": paper.keywords,
            "url": paper.url,
            "notes_preview": paper.notes_preview,
            "reading_status": paper.reading_status,
            "reading_progress": paper.reading_progress,
            "pdf_path": paper.pdf_path,
            "created_by": paper.created_by,
            "created_at": paper.created_at,
            "updated_at": paper.updated_at,
            "creator_name": current_user.username,
            "tags": tags
        }

        return success_response(
            data=paper_dict,
            message="论文更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新论文失败: {str(e)}"
        )


@router.delete("/{paper_id}", response_model=dict)
async def delete_paper(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除论文（软删除）

    - 需要登录
    - 只能删除自己创建的论文（管理员可以删除所有论文）
    - 实际上是标记为已删除，不会真正删除数据
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
        if not check_permission(current_user, paper.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此论文"
            )

        # 软删除（设置删除时间）
        paper.deleted_at = datetime.utcnow()
        paper.updated_at = datetime.utcnow()

        await db.commit()

        return success_response(message="论文删除成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除论文失败: {str(e)}"
        )


@router.get("/{paper_id}/download", response_class=Response)
async def download_paper_pdf(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载论文PDF文件

    - 需要登录
    - 只能下载自己的论文或管理员可下载所有论文
    """
    try:
        # 查询论文
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

        # 权限检查
        if not check_permission(current_user, paper.created_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权下载此论文"
            )

        # 检查是否有PDF文件
        if not paper.pdf_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该论文没有PDF文件"
            )

        # 检查文件是否存在
        if not os.path.exists(paper.pdf_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF文件不存在"
            )

        # 读取文件内容
        with open(paper.pdf_path, "rb") as f:
            file_content = f.read()

        # 生成下载文件名（使用论文标题）
        # 清理文件名中的非法字符
        safe_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_title}.pdf" if safe_title else f"paper_{paper_id}.pdf"

        return Response(
            content=file_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载PDF失败: {str(e)}"
        )


@router.get("/{paper_id}/export/bibtex", response_class=Response)
async def export_paper_bibtex(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出单篇论文为BibTeX格式

    - 需要登录
    - 只能导出自己的论文或管理员可导出所有论文
    """
    try:
        # 查询论文
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

        # 权限检查
        if paper.created_by != current_user.id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权导出此论文"
            )

        # 生成BibTeX内容
        bibtex_content = generate_bibtex_entry(paper)

        # 生成文件名
        filename = f"paper_{paper_id}.bib"

        return Response(
            content=bibtex_content.encode('utf-8'),
            media_type="application/x-bibtex",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出BibTeX失败: {str(e)}"
        )


@router.post("/export/bibtex/batch", response_class=Response)
async def export_papers_bibtex_batch(
    paper_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量导出多篇论文为BibTeX格式

    - 需要登录
    - 只能导出自己的论文或管理员可导出所有论文
    """
    try:
        # 查询论文
        paper_query = select(Paper).where(
            and_(
                Paper.id.in_(paper_ids),
                Paper.deleted_at.is_(None)
            )
        )
        paper_result = await db.execute(paper_query)
        papers = paper_result.scalars().all()

        if not papers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到论文"
            )

        # 权限检查：过滤出用户有权访问的论文
        accessible_papers = []
        for paper in papers:
            if paper.created_by == current_user.id or current_user.role == 'admin':
                accessible_papers.append(paper)

        if not accessible_papers:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权导出这些论文"
            )

        # 生成BibTeX内容（批量）
        bibtex_entries = []
        for paper in accessible_papers:
            bibtex_entries.append(generate_bibtex_entry(paper))

        bibtex_content = "\n\n".join(bibtex_entries)

        # 生成文件名
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"papers_export_{timestamp}.bib"

        return Response(
            content=bibtex_content.encode('utf-8'),
            media_type="application/x-bibtex",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导出BibTeX失败: {str(e)}"
        )


@router.get("/export/bibtex/all", response_class=Response)
async def export_all_papers_bibtex(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出当前用户的所有论文为BibTeX格式

    - 需要登录
    - 导出用户自己的所有论文
    """
    try:
        # 查询用户的所有论文
        paper_query = select(Paper).where(
            and_(
                Paper.created_by == current_user.id,
                Paper.deleted_at.is_(None)
            )
        ).order_by(desc(Paper.year), Paper.title)

        paper_result = await db.execute(paper_query)
        papers = paper_result.scalars().all()

        if not papers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="没有可导出的论文"
            )

        # 生成BibTeX内容
        bibtex_entries = []
        for paper in papers:
            bibtex_entries.append(generate_bibtex_entry(paper))

        bibtex_content = "\n\n".join(bibtex_entries)

        # 生成文件名
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"my_papers_{timestamp}.bib"

        return Response(
            content=bibtex_content.encode('utf-8'),
            media_type="application/x-bibtex",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出所有论文BibTeX失败: {str(e)}"
        )


def generate_bibtex_entry(paper: Paper) -> str:
    """
    生成单篇论文的BibTeX条目

    Args:
        paper: 论文对象

    Returns:
        BibTeX格式的字符串
    """
    # 生成citation key: 第一作者姓氏+年份
    # 简化处理：取第一个作者的第一个单词
    if paper.authors:
        first_author = paper.authors.split(',')[0].strip().split()[-1]
        citation_key = f"{first_author}{paper.year or 'n.d.'}"
    else:
        citation_key = f"paper{paper.id}"

    # 清理特殊字符
    citation_key = "".join(c for c in citation_key if c.isalnum())

    # 确定文献类型（默认article）
    entry_type = "article"

    # 构建BibTeX条目
    bibtex = f"@{entry_type}{{{citation_key},\n"

    # 必需字段
    if paper.title:
        bibtex += f"  title = {{{paper.title}}},\n"

    if paper.authors:
        bibtex += f"  author = {{{paper.authors}}},\n"

    if paper.year:
        bibtex += f"  year = {{{paper.year}}},\n"

    # 期刊相关字段
    if paper.journal:
        bibtex += f"  journal = {{{paper.journal}}},\n"

    if paper.volume:
        bibtex += f"  volume = {{{paper.volume}}},\n"

    if paper.issue:
        bibtex += f"  number = {{{paper.issue}}},\n"

    if paper.pages:
        bibtex += f"  pages = {{{paper.pages}}},\n"

    # 可选字段
    if paper.doi:
        bibtex += f"  doi = {{{paper.doi}}},\n"

    if paper.url:
        bibtex += f"  url = {{{paper.url}}},\n"

    if paper.abstract:
        # 转义大括号和特殊字符
        abstract_escaped = paper.abstract.replace('{', '\\{').replace('}', '\\}')
        bibtex += f"  abstract = {{{abstract_escaped}}},\n"

    if paper.keywords:
        bibtex += f"  keywords = {{{paper.keywords}}},\n"

    # 移除最后一个逗号
    bibtex = bibtex.rstrip(',\n') + "\n"
    bibtex += "}"

    return bibtex


@router.post("/import/bibtex", response_model=dict)
async def import_bibtex(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    从BibTeX文件导入论文

    - 需要登录
    - 上传.bib文件
    - 批量创建论文记录
    - 返回导入结果统计
    """
    try:
        # 验证文件类型
        if not file.filename.endswith(('.bib', '.bibtex')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仅支持.bib或.bibtex文件"
            )

        # 读取文件内容
        content = await file.read()
        bibtex_content = content.decode('utf-8', errors='ignore')

        # 解析BibTeX文件
        entries = parse_bibtex(bibtex_content)

        if not entries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="BibTeX文件中没有找到有效条目"
            )

        # 批量创建论文
        success_count = 0
        fail_count = 0
        errors = []
        created_papers = []

        for entry in entries:
            try:
                # 创建论文对象
                paper = Paper(
                    title=entry.get('title', ''),
                    authors=entry.get('author', entry.get('authors', '')),
                    journal=entry.get('journal', ''),
                    year=entry.get('year'),
                    volume=entry.get('volume', ''),
                    issue=entry.get('number', ''),
                    pages=entry.get('pages', ''),
                    doi=entry.get('doi', ''),
                    url=entry.get('url', ''),
                    abstract=entry.get('abstract', ''),
                    keywords=entry.get('keywords', ''),
                    reading_status='unread',
                    reading_progress=0,
                    created_by=current_user.id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                db.add(paper)
                await db.flush()  # 获取paper.id但不提交

                created_papers.append({
                    'id': paper.id,
                    'title': paper.title,
                    'authors': paper.authors
                })

                success_count += 1

            except Exception as e:
                fail_count += 1
                errors.append({
                    'title': entry.get('title', 'Unknown'),
                    'error': str(e)
                })

        # 提交所有成功的论文
        await db.commit()

        return success_response(
            message=f"导入完成：成功{success_count}篇，失败{fail_count}篇",
            data={
                'total': len(entries),
                'success_count': success_count,
                'fail_count': fail_count,
                'created_papers': created_papers,
                'errors': errors if errors else None
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入BibTeX失败: {str(e)}"
        )


def parse_bibtex(content: str) -> List[dict]:
    """
    简单的BibTeX解析器

    Args:
        content: BibTeX文件内容

    Returns:
        解析后的条目列表
    """
    entries = []

    # 使用正则表达式匹配BibTeX条目
    # 匹配 @article{key, ... }
    pattern = r'@(\w+)\s*\{\s*([^,]+)\s*,\s*(.*?)\n\}'

    matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        entry_type = match.group(1).lower()
        citation_key = match.group(2).strip()
        fields_str = match.group(3)

        # 解析字段
        entry = {'entry_type': entry_type, 'citation_key': citation_key}

        # 匹配字段: field = {value} 或 field = "value"
        field_pattern = r'(\w+)\s*=\s*[{"](.*?)["}]\s*(?:,|\n)'
        field_matches = re.finditer(field_pattern, fields_str, re.DOTALL)

        for field_match in field_matches:
            field_name = field_match.group(1).lower()
            field_value = field_match.group(2).strip()

            # 清理值：移除多余空白和换行
            field_value = ' '.join(field_value.split())

            entry[field_name] = field_value

        # 确保必需字段存在
        if 'title' in entry or 'author' in entry:
            entries.append(entry)

    return entries
