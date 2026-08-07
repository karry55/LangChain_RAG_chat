"""对话 & 会话相关 Pydantic 模型"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(None, description="会话ID (空则新建)")
    message: str = Field(..., min_length=1, max_length=5000, description="用户问题")
    top_k: int = Field(5, ge=1, le=10, description="检索片段数")


class SourceItem(BaseModel):
    document_title: str
    chunk_index: int
    content: str
    score: float


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    sources: Optional[List[SourceItem]] = None
    token_count: int = 0
    feedback: Optional[str] = None
    created_at: str


class ConversationResponse(BaseModel):
    id: str
    title: str
    message_count: int
    created_at: str
    updated_at: str


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int


class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="消息ID")
    feedback: str = Field(..., pattern="^(like|dislike)$", description="like 或 dislike")
