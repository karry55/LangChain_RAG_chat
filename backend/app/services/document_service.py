"""文档管理服务"""
import os
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.core.config import get_settings
from app.models.knowledge import KnowledgeDocument, DocumentChunk
from app.rag.loader import load_document
from app.rag.splitter import split_documents
from app.rag.vector_store import add_documents

settings = get_settings()


async def create_document(
    db: AsyncSession,
    filename: str,
    file_type: str,
    file_size: int,
    file_path: str,
    uploaded_by: str,
) -> KnowledgeDocument:
    """创建文档记录"""
    doc = KnowledgeDocument(
        title=filename,
        file_type=file_type,
        file_size=file_size,
        file_path=file_path,
        status="pending",
        uploaded_by=uploaded_by,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


async def process_document(doc_id: str, db: AsyncSession):
    """异步处理文档: 加载 → 分块 → 嵌入 → 存储"""
    # 获取文档
    result = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        logger.error(f"文档不存在: {doc_id}")
        return

    try:
        # 更新状态为处理中
        doc.status = "processing"
        await db.commit()

        # 1. 加载文档
        logger.info(f"[{doc.title}] 开始加载...")
        raw_docs = load_document(doc.file_path, doc.file_type)

        # 2. 分块
        logger.info(f"[{doc.title}] 开始分块...")
        chunks = split_documents(raw_docs)

        # 3. 为每个 chunk 注入 document_id 元数据（用于后续删除和过滤）
        for chunk in chunks:
            chunk.metadata["document_id"] = doc_id
            chunk.metadata["doc_title"] = doc.title

        # 4. 存储到向量数据库 (Chroma 内部使用 embedding_function 统一嵌入)
        logger.info(f"[{doc.title}] 存储向量到 {settings.vector_store} (含嵌入)...")
        vector_ids = add_documents(chunks)

        # 4. 保存块元数据到 PostgreSQL
        for i, chunk in enumerate(chunks):
            chunk_record = DocumentChunk(
                document_id=doc_id,
                chunk_index=i,
                content=chunk.page_content,
                vector_id=str(vector_ids[i]) if i < len(vector_ids) else "",
                token_count=len(chunk.page_content),
            )
            db.add(chunk_record)

        # 更新文档状态
        doc.status = "completed"
        doc.chunk_count = len(chunks)
        await db.commit()

        logger.info(f"[{doc.title}] 处理完成! 共 {len(chunks)} 个块")

    except Exception as e:
        logger.error(f"[{doc.title}] 处理失败: {e}")
        doc.status = "failed"
        doc.error_message = str(e)
        await db.commit()


async def get_documents(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """分页获取文档列表"""
    offset = (page - 1) * page_size

    total_result = await db.execute(select(func.count(KnowledgeDocument.id)))
    total = total_result.scalar()

    result = await db.execute(
        select(KnowledgeDocument)
        .order_by(KnowledgeDocument.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    documents = result.scalars().all()

    return {
        "documents": documents,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_document_chunks(
    db: AsyncSession,
    doc_id: str,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    """分页获取文档的切块列表"""
    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == doc_id)
    )
    total = total_result.scalar()

    result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == doc_id)
        .order_by(DocumentChunk.chunk_index)
        .offset(offset)
        .limit(page_size)
    )
    chunks = result.scalars().all()

    return {"chunks": chunks, "total": total}


async def delete_document(doc_id: str, db: AsyncSession):
    """删除文档及其向量数据"""
    result = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        return

    # 删除向量数据
    try:
        from app.rag.vector_store import delete_documents_by_filter
        delete_documents_by_filter({"document_id": doc_id})
    except Exception as e:
        logger.warning(f"删除向量数据失败: {e}")

    # 删除文件
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # 删除数据库记录 (级联删除 chunks)
    await db.delete(doc)
    await db.commit()
    logger.info(f"文档已删除: {doc.title}")


async def get_knowledge_stats(db: AsyncSession) -> dict:
    """获取知识库统计数据"""
    total = await db.execute(select(func.count(KnowledgeDocument.id)))
    processed = await db.execute(
        select(func.count(KnowledgeDocument.id)).where(
            KnowledgeDocument.status == "completed"
        )
    )
    failed = await db.execute(
        select(func.count(KnowledgeDocument.id)).where(
            KnowledgeDocument.status == "failed"
        )
    )
    total_chunks = await db.execute(select(func.count(DocumentChunk.id)))
    total_size = await db.execute(
        select(func.sum(KnowledgeDocument.file_size))
    )

    return {
        "total_documents": total.scalar() or 0,
        "processed_documents": processed.scalar() or 0,
        "failed_documents": failed.scalar() or 0,
        "total_chunks": total_chunks.scalar() or 0,
        "total_file_size": total_size.scalar() or 0,
    }
