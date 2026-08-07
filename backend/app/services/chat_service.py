"""对话服务: 会话管理 + 消息管理"""
from typing import List, Optional, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from loguru import logger

from app.models.conversation import Conversation, Message
from app.rag.chain import rag_chain


async def get_or_create_conversation(
    db: AsyncSession,
    user_id: str,
    conversation_id: Optional[str] = None,
    title: str = "新对话",
) -> Conversation:
    """获取已有会话或创建新会话"""
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        conv = result.scalar_one_or_none()
        if conv:
            return conv

    # 创建新会话
    conv = Conversation(user_id=user_id, title=title[:200])
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return conv


async def chat_stream(
    db: AsyncSession,
    user_id: str,
    question: str,
    conversation_id: Optional[str] = None,
) -> AsyncIterator[dict]:
    """执行流式问答

    Yields:
        dict: SSE 事件 {"type":"token"|"sources"|"done", ...}
    """
    # 1. 获取或创建会话
    conv = await get_or_create_conversation(
        db, user_id, conversation_id,
        title=question[:30] if not conversation_id else "新对话",
    )

    # 2. 保存用户消息
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=question,
    )
    db.add(user_msg)

    # 更新会话标题（仅首次）
    if conv.message_count == 0:
        conv.title = question[:30] + ("..." if len(question) > 30 else "")
    await db.flush()

    # 3. 获取历史消息
    history = await get_conversation_history(db, conv.id, limit=10)

    # 4. 执行 RAG
    full_answer = ""
    sources = []

    async for event in rag_chain.query(question, history):
        if event["type"] == "token":
            full_answer += event["content"]
        elif event["type"] == "sources":
            sources = event["sources"]

        # 每个事件都返回，同时附加 conversation_id
        yield {
            **event,
            "conversation_id": conv.id,
        }

    # 5. 保存 AI 回复
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=full_answer,
        sources=sources,
        token_count=len(full_answer),
    )
    db.add(assistant_msg)
    await db.flush()
    # 原子更新消息计数（避免并发丢失更新）
    from sqlalchemy import update as sql_update
    await db.execute(
        sql_update(Conversation)
        .where(Conversation.id == conv.id)
        .values(message_count=Conversation.message_count + 2)
    )

    logger.info(f"会话 {conv.id}: 问答完成, 回答长度 {len(full_answer)}")


async def get_conversation_history(
    db: AsyncSession,
    conversation_id: str,
    limit: int = 20,
) -> List[dict]:
    """获取会话的历史消息"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    messages.reverse()

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]


async def get_user_conversations(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    """分页获取用户的会话列表"""
    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
    )
    total = total_result.scalar()

    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.updated_at))
        .offset(offset)
        .limit(page_size)
    )
    conversations = result.scalars().all()

    return {
        "conversations": conversations,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_conversation_messages(
    db: AsyncSession,
    conversation_id: str,
    user_id: str,
    page: int = 1,
    page_size: int = 100,
) -> dict:
    """获取会话的消息列表（需验证归属）"""
    # 验证会话归属
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conv = conv_result.scalar_one_or_none()
    if conv is None:
        return {"messages": [], "total": 0}

    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    )
    total = total_result.scalar()

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(offset)
        .limit(page_size)
    )
    messages = result.scalars().all()

    return {"messages": messages, "total": total}


async def delete_conversation(
    db: AsyncSession,
    conversation_id: str,
    user_id: str,
):
    """删除会话（需验证归属）"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conv = result.scalar_one_or_none()
    if conv:
        await db.delete(conv)
        await db.commit()


async def set_feedback(
    db: AsyncSession,
    message_id: str,
    feedback: str,
    user_id: str,
):
    """设置消息反馈 (like/dislike)，校验消息归属"""
    from app.models.conversation import Conversation as ConvModel
    result = await db.execute(
        select(Message)
        .join(ConvModel, Message.conversation_id == ConvModel.id)
        .where(Message.id == message_id, ConvModel.user_id == user_id)
    )
    msg = result.scalar_one_or_none()
    if msg:
        msg.feedback = feedback
        db.add(msg)
        await db.flush()
