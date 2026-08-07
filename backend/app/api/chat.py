"""问答接口 - SSE 流式对话"""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, FeedbackRequest
from app.services.chat_service import chat_stream, set_feedback

router = APIRouter()


@router.post("/query")
async def chat_query(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送问题，SSE 流式返回回答"""

    async def event_stream():
        """SSE 事件流生成器"""
        try:
            async for event in chat_stream(
                db=db,
                user_id=current_user.id,
                question=data.message,
                conversation_id=data.conversation_id,
            ):
                # 将事件转为 SSE 格式
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_event = {
                "type": "error",
                "content": str(e),
                "conversation_id": data.conversation_id,
            }
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
        finally:
            await db.commit()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )


@router.post("/feedback")
async def chat_feedback(
    data: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """对回答进行反馈 (点赞/踩)"""
    await set_feedback(db, data.message_id, data.feedback)
    return {"message": "反馈已记录"}
