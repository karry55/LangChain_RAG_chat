"""知识库管理接口 (仅管理员)"""
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.core.config import get_settings
from app.models.user import User
from app.services.document_service import (
    create_document,
    process_document,
    get_documents,
    get_document_chunks,
    delete_document,
    get_knowledge_stats,
)

router = APIRouter()
settings = get_settings()

ALLOWED_EXTENSIONS = {"pdf", "docx", "xlsx", "csv", "txt", "md"}


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: str = Form(""),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """上传文档到知识库 (异步处理)"""
    # 校验文件类型
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: .{ext}，支持: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 校验文件大小
    contents = await file.read()
    file_size = len(contents)
    if file_size > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大 {settings.max_upload_size_mb}MB",
        )

    # 保存文件
    file_id = str(uuid.uuid4())
    save_path = os.path.join(settings.upload_dir, f"{file_id}.{ext}")
    os.makedirs(settings.upload_dir, exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(contents)

    # 创建文档记录
    doc = await create_document(
        db=db,
        filename=file.filename,
        file_type=ext,
        file_size=file_size,
        file_path=save_path,
        uploaded_by=admin.id,
    )
    doc.description = description
    await db.commit()

    # 后台异步处理文档
    background_tasks.add_task(process_document_with_db, doc.id)

    return {
        "document_id": doc.id,
        "status": doc.status,
        "message": f"文档 '{file.filename}' 已上传，正在后台处理...",
    }


async def process_document_with_db(doc_id: str):
    """后台任务：处理文档（需要独立的数据库会话）"""
    from app.core.database import async_session

    async with async_session() as db:
        try:
            await process_document(doc_id, db)
        except Exception as e:
            from loguru import logger
            logger.error(f"后台处理文档失败 {doc_id}: {e}")


@router.get("/documents")
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取知识库文档列表"""
    result = await get_documents(db, page, page_size)
    return {
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "description": d.description,
                "file_type": d.file_type,
                "file_size": d.file_size,
                "status": d.status,
                "chunk_count": d.chunk_count,
                "error_message": d.error_message,
                "uploaded_by": d.uploaded_by,
                "created_at": str(d.created_at),
                "updated_at": str(d.updated_at),
            }
            for d in result["documents"]
        ],
        "total": result["total"],
    }


@router.get("/documents/{doc_id}/chunks")
async def list_chunks(
    doc_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文档的切块列表"""
    result = await get_document_chunks(db, doc_id, page, page_size)
    return {
        "chunks": [
            {
                "id": c.id,
                "document_id": c.document_id,
                "chunk_index": c.chunk_index,
                "content": c.content,
                "token_count": c.token_count,
                "created_at": str(c.created_at),
            }
            for c in result["chunks"]
        ],
        "total": result["total"],
    }


@router.delete("/documents/{doc_id}")
async def remove_document(
    doc_id: str,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """删除文档及其所有数据"""
    await delete_document(doc_id, db)
    return {"message": "文档已删除"}


@router.get("/stats")
async def knowledge_stats(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取知识库统计数据"""
    return await get_knowledge_stats(db)
