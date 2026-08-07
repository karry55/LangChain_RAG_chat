"""FastAPI 应用入口"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import get_settings
from app.core.database import init_db
from app.models import Base  # noqa: F401 - 确保所有模型被导入

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")

    # 创建管理员账户
    await _ensure_admin()

    # 确保上传目录存在
    os.makedirs(settings.upload_dir, exist_ok=True)

    logger.info(f"RAG 知识库系统启动完成! 访问 http://localhost:{settings.backend_port}/docs 查看API文档")
    yield
    # 关闭时
    logger.info("应用正在关闭...")


async def _ensure_admin():
    """确保管理员账户存在"""
    from app.core.security import hash_password
    from app.core.database import async_session
    from sqlalchemy import select
    from app.models.user import User

    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if admin is None:
            admin = User(
                username="admin",
                password_hash=hash_password("123456"),
                email="admin@rag-system.com",
                role="admin",
            )
            db.add(admin)
            await db.commit()
            logger.info("管理员账户已创建: admin / 123456")
        else:
            logger.info("管理员账户已存在")


# 创建 FastAPI 应用
app = FastAPI(
    title="RAG 企业级知识库问答系统",
    description="基于 LangChain + 阿里云百炼的 RAG 知识库问答 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from app.api import auth, chat, conversation, knowledge, user
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api/chat", tags=["问答"])
app.include_router(conversation.router, prefix="/api/conversations", tags=["会话"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(user.router, prefix="/api/users", tags=["用户"])


@app.get("/")
async def root():
    return {
        "message": "RAG 企业级知识库问答系统 API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
