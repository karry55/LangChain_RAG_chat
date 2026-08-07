"""知识库相关 Pydantic 模型"""
from pydantic import BaseModel
from typing import Optional, List


class DocumentResponse(BaseModel):
    id: str
    title: str
    description: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: str
    uploaded_by: str
    created_at: str
    updated_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


class ChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    content: str
    token_count: int
    created_at: str


class KnowledgeStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    processed_documents: int
    failed_documents: int
    total_file_size: int

class DocumentUploadResponse(BaseModel):
    document_id: str
    status: str
    message: str
