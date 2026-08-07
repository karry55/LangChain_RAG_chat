"""会话管理接口"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.chat_service import (
    get_user_conversations,
    get_conversation_messages,
    delete_conversation,
)

router = APIRouter()


@router.get("")
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的会话列表"""
    result = await get_user_conversations(db, current_user.id, page, page_size)
    return {
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "message_count": c.message_count,
                "created_at": str(c.created_at),
                "updated_at": str(c.updated_at),
            }
            for c in result["conversations"]
        ],
        "total": result["total"],
    }


@router.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定会话的消息列表"""
    result = await get_conversation_messages(
        db, conversation_id, current_user.id, page, page_size
    )
    return {
        "messages": [
            {
                "id": m.id,
                "conversation_id": m.conversation_id,
                "role": m.role,
                "content": m.content,
                "sources": m.sources,
                "token_count": m.token_count,
                "feedback": m.feedback,
                "created_at": str(m.created_at),
            }
            for m in result["messages"]
        ],
        "total": result["total"],
    }


@router.delete("/{conversation_id}")
async def remove_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除指定会话"""
    await delete_conversation(db, conversation_id, current_user.id)
    return {"message": "会话已删除"}
