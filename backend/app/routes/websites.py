"""
网站收集相关的API路由

提供科研常用网站的CRUD操作
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.utils.dependencies import get_current_user, get_db
from app.utils.response import success_response, error_response
from app.models.database import User

router = APIRouter(prefix="/api/websites", tags=["websites"])


def format_datetime(dt):
    """格式化datetime对象为ISO字符串"""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)


@router.post("/")
async def create_website(
    name: str = Query(..., description="网站名称"),
    url: str = Query(..., description="网站URL"),
    category: Optional[str] = Query(None, description="网站分类"),
    description: Optional[str] = Query(None, description="网站描述"),
    is_favorite: bool = Query(False, description="是否收藏"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新网站
    """
    try:
        now = datetime.utcnow().isoformat()

        # 插入数据
        query = text("""
            INSERT INTO websites (user_id, name, url, category, description, is_favorite, created_at)
            VALUES (:user_id, :name, :url, :category, :description, :is_favorite, :created_at)
        """)

        result = await db.execute(
            query,
            {
                "user_id": current_user.id,
                "name": name,
                "url": url,
                "category": category,
                "description": description,
                "is_favorite": 1 if is_favorite else 0,
                "created_at": now
            }
        )

        website_id = result.lastrowid
        await db.commit()

        # 查询创建的网站
        select_query = text("""
            SELECT id, user_id, name, url, category, description, is_favorite, created_at, updated_at
            FROM websites
            WHERE id = :id AND deleted_at IS NULL
        """)

        result = await db.execute(select_query, {"id": website_id})
        website = result.fetchone()

        if not website:
            raise HTTPException(status_code=404, detail="网站创建失败")

        website_dict = {
            "id": website[0],
            "user_id": website[1],
            "name": website[2],
            "url": website[3],
            "category": website[4],
            "description": website[5],
            "is_favorite": bool(website[6]),
            "created_at": format_datetime(website[7]),
            "updated_at": format_datetime(website[8])
        }

        return success_response(data=website_dict, message="网站添加成功")

    except Exception as e:
        await db.rollback()
        print(f"Error creating website: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(message=f"添加网站失败: {str(e)}")


@router.get("/")
async def get_websites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(1000, ge=1, le=1000, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    is_favorite: Optional[bool] = Query(None, description="是否只显示收藏"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取网站列表（支持搜索、筛选、分页）

    管理员可以查看所有网站，普通用户只能查看自己创建的网站
    """
    try:
        # 构建查询条件
        conditions = ["deleted_at IS NULL"]
        params = {"user_id": current_user.id}

        # 权限控制：普通用户只能看到自己创建的，管理员可以看到所有的
        if current_user.role != "admin":
            conditions.append("user_id = :user_id")

        # 搜索关键词
        if keyword:
            conditions.append("(name LIKE :keyword OR description LIKE :keyword OR url LIKE :keyword)")
            params["keyword"] = f"%{keyword}%"

        # 分类筛选
        if category:
            conditions.append("category = :category")
            params["category"] = category

        # 收藏筛选
        if is_favorite is not None:
            conditions.append("is_favorite = :is_favorite")
            params["is_favorite"] = 1 if is_favorite else 0

        where_clause = " AND ".join(conditions)

        # 查询总数
        count_query = text(f"""
            SELECT COUNT(*) FROM websites
            WHERE {where_clause}
        """)

        result = await db.execute(count_query, params)
        total = result.scalar() or 0

        # 查询列表
        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        list_query = text(f"""
            SELECT id, user_id, name, url, category, description, is_favorite, created_at, updated_at
            FROM websites
            WHERE {where_clause}
            ORDER BY is_favorite DESC, created_at DESC
            LIMIT :limit OFFSET :offset
        """)

        result = await db.execute(list_query, params)
        websites = result.fetchall()

        websites_list = []
        for website in websites:
            websites_list.append({
                "id": website[0],
                "user_id": website[1],
                "name": website[2],
                "url": website[3],
                "category": website[4],
                "description": website[5],
                "is_favorite": bool(website[6]),
                "created_at": format_datetime(website[7]),
                "updated_at": format_datetime(website[8])
            })

        return success_response(data={
            "websites": websites_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })

    except Exception as e:
        print(f"Error getting websites: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(message=f"获取网站列表失败: {str(e)}")


@router.get("/categories")
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有分类列表
    """
    try:
        # 权限控制
        conditions = "deleted_at IS NULL"
        params = {}

        if current_user.role != "admin":
            conditions += " AND user_id = :user_id"
            params["user_id"] = current_user.id

        query = text(f"""
            SELECT DISTINCT category
            FROM websites
            WHERE {conditions} AND category IS NOT NULL AND category != ''
            ORDER BY category
        """)

        result = await db.execute(query, params)
        categories = [row[0] for row in result.fetchall()]

        return success_response(data={"categories": categories})

    except Exception as e:
        print(f"Error getting categories: {str(e)}")
        return error_response(message=f"获取分类列表失败: {str(e)}")


@router.get("/{website_id}")
async def get_website(
    website_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取网站详情
    """
    try:
        query = text("""
            SELECT id, user_id, name, url, category, description, is_favorite, created_at, updated_at
            FROM websites
            WHERE id = :id AND deleted_at IS NULL
        """)

        result = await db.execute(query, {"id": website_id})
        website = result.fetchone()

        if not website:
            raise HTTPException(status_code=404, detail="网站不存在")

        # 权限检查：只有创建者和管理员可以查看
        if website[1] != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="无权访问此网站")

        website_dict = {
            "id": website[0],
            "user_id": website[1],
            "name": website[2],
            "url": website[3],
            "category": website[4],
            "description": website[5],
            "is_favorite": bool(website[6]),
            "created_at": format_datetime(website[7]),
            "updated_at": format_datetime(website[8])
        }

        return success_response(data=website_dict)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting website: {str(e)}")
        return error_response(message=f"获取网站详情失败: {str(e)}")


@router.put("/{website_id}")
async def update_website(
    website_id: int,
    name: Optional[str] = Query(None, description="网站名称"),
    url: Optional[str] = Query(None, description="网站URL"),
    category: Optional[str] = Query(None, description="网站分类"),
    description: Optional[str] = Query(None, description="网站描述"),
    is_favorite: Optional[bool] = Query(None, description="是否收藏"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新网站信息
    """
    try:
        # 检查网站是否存在
        check_query = text("""
            SELECT user_id FROM websites
            WHERE id = :id AND deleted_at IS NULL
        """)

        result = await db.execute(check_query, {"id": website_id})
        website = result.fetchone()

        if not website:
            raise HTTPException(status_code=404, detail="网站不存在")

        # 权限检查：只有创建者和管理员可以编辑
        if website[0] != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="无权编辑此网站")

        # 构建更新字段
        update_fields = []
        params = {"id": website_id, "updated_at": datetime.utcnow().isoformat()}

        if name is not None:
            update_fields.append("name = :name")
            params["name"] = name

        if url is not None:
            update_fields.append("url = :url")
            params["url"] = url

        if category is not None:
            update_fields.append("category = :category")
            params["category"] = category

        if description is not None:
            update_fields.append("description = :description")
            params["description"] = description

        if is_favorite is not None:
            update_fields.append("is_favorite = :is_favorite")
            params["is_favorite"] = 1 if is_favorite else 0

        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供任何更新字段")

        update_fields.append("updated_at = :updated_at")

        # 执行更新
        update_query = text(f"""
            UPDATE websites
            SET {", ".join(update_fields)}
            WHERE id = :id AND deleted_at IS NULL
        """)

        await db.execute(update_query, params)
        await db.commit()

        # 返回更新后的数据
        select_query = text("""
            SELECT id, user_id, name, url, category, description, is_favorite, created_at, updated_at
            FROM websites
            WHERE id = :id AND deleted_at IS NULL
        """)

        result = await db.execute(select_query, {"id": website_id})
        website = result.fetchone()

        website_dict = {
            "id": website[0],
            "user_id": website[1],
            "name": website[2],
            "url": website[3],
            "category": website[4],
            "description": website[5],
            "is_favorite": bool(website[6]),
            "created_at": format_datetime(website[7]),
            "updated_at": format_datetime(website[8])
        }

        return success_response(data=website_dict, message="网站更新成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error updating website: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(message=f"更新网站失败: {str(e)}")


@router.delete("/{website_id}")
async def delete_website(
    website_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除网站（软删除）
    """
    try:
        # 检查网站是否存在
        check_query = text("""
            SELECT user_id FROM websites
            WHERE id = :id AND deleted_at IS NULL
        """)

        result = await db.execute(check_query, {"id": website_id})
        website = result.fetchone()

        if not website:
            raise HTTPException(status_code=404, detail="网站不存在")

        # 权限检查：只有创建者和管理员可以删除
        if website[0] != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="无权删除此网站")

        # 软删除
        delete_query = text("""
            UPDATE websites
            SET deleted_at = :deleted_at
            WHERE id = :id
        """)

        await db.execute(delete_query, {
            "id": website_id,
            "deleted_at": datetime.utcnow().isoformat()
        })

        await db.commit()

        return success_response(message="网站删除成功")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error deleting website: {str(e)}")
        return error_response(message=f"删除网站失败: {str(e)}")
