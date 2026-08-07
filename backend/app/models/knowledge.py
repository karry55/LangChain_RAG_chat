"""知识库文档 & 文档块模型"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class KnowledgeDocument(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf/docx/xlsx/csv/txt/md
    file_path: Mapped[str] = mapped_column(String(1000), default="")
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending/processing/completed/failed
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, default="")
    uploaded_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关联
    uploader = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    vector_id: Mapped[str] = mapped_column(String(255), default="")
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关联
    document = relationship("KnowledgeDocument", back_populates="chunks")

    __table_args__ = (UniqueConstraint("document_id", "chunk_index"),)
