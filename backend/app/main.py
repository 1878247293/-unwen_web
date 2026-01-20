"""
FastAPI主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.models import init_db, close_db


# 创建必要的目录
os.makedirs("data/uploads/papers", exist_ok=True)
os.makedirs("data/uploads/pdfs", exist_ok=True)
os.makedirs("data/uploads/avatars", exist_ok=True)
os.makedirs("data/backups", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print(f"正在启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()

    # 创建默认管理员账号
    from app.services.user_service import create_default_admin
    await create_default_admin()

    yield

    # 关闭时执行
    await close_db()
    print(f"{settings.APP_NAME} 已停止")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="科研论文整理与总结网站API",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")


# 根路由
@app.get("/")
async def root():
    """根路由"""
    return {
        "message": f"欢迎使用 {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# 导入并注册路由
from app.routes import auth, users, papers, stats, tags, reading, notes, comments, suggestions, notifications, ideas, websites, discussions, system

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(papers.router, prefix="/api", tags=["论文"])
app.include_router(stats.router, prefix="/api", tags=["统计"])
app.include_router(tags.router, prefix="/api", tags=["标签"])
app.include_router(reading.router, prefix="/api", tags=["阅读"])
app.include_router(notes.router, prefix="/api", tags=["笔记"])
app.include_router(comments.router, prefix="/api", tags=["评论"])
app.include_router(suggestions.router, prefix="/api", tags=["改进建议"])
app.include_router(notifications.router, prefix="/api", tags=["通知"])
app.include_router(ideas.router, prefix="/api/ideas", tags=["想法"])
app.include_router(websites.router, tags=["网站收集"])
app.include_router(discussions.router, prefix="/api", tags=["讨论"])
app.include_router(system.router, prefix="/api", tags=["系统监控"])

# 稍后添加更多路由
# from app.routes import notes, tags, ai
# app.include_router(notes.router, prefix="/api/notes", tags=["笔记"])
# app.include_router(tags.router, prefix="/api/tags", tags=["标签"])
# app.include_router(ai.router, prefix="/api/ai", tags=["AI助手"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
