"""问答接口 - SSE 流式对话"""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.database import async_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, FeedbackRequest
from app.services.chat_service import chat_stream, set_feedback

router = APIRouter()


@router.post("/query")
async def chat_query(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """发送问题，SSE 流式返回回答

    注意：不使用 Depends(get_db) 因为 StreamingResponse 的生命周期
    与 FastAPI 依赖注入不兼容。改为在 event_stream 内部手动管理 session。
    """
    async def event_stream():
        """SSE 事件流生成器 — 自行管理数据库会话生命周期"""
        async with async_session() as db:
            try:
                async for event in chat_stream(
                    db=db,
                    user_id=current_user.id,
                    question=data.message,
                    conversation_id=data.conversation_id,
                ):
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            except Exception as e:
                error_event = {
                    "type": "error",
                    "content": str(e),
                    "conversation_id": data.conversation_id,
                }
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/feedback")
async def chat_feedback(
    data: FeedbackRequest,
    current_user: User = Depends(get_current_user),
):
    """对回答进行反馈 (点赞/踩)"""
    async with async_session() as db:
        await set_feedback(db, data.message_id, data.feedback, current_user.id)
        await db.commit()
    return {"message": "反馈已记录"}
