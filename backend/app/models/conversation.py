"""会话 & 消息模型"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), default="新对话")
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关联
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan",
                            order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(10), nullable=False)  # user | assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[dict] = mapped_column(JSON, nullable=True, default=None)
    # sources 结构: [{"document_title":"...","chunk_index":0,"content":"...","score":0.92}, ...]
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    feedback: Mapped[str] = mapped_column(String(10), nullable=True, default=None)  # null | like | dislike
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关联
    conversation = relationship("Conversation", back_populates="messages")
