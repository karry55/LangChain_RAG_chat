"""用户管理接口"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/me")
async def get_my_info(current_user: User = Depends(get_admin_user)):
    """获取当前用户信息（已在 auth/me 中实现，此处兼容）"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": str(current_user.created_at),
    }


@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表 (仅管理员)"""
    offset = (page - 1) * page_size

    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar()

    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": str(u.created_at),
            }
            for u in users
        ],
        "total": total,
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """删除用户 (仅管理员，不能删除自己)"""
    if user_id == admin.id:
        return {"message": "不能删除自己的账户"}

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return {"message": "用户不存在"}

    # 不允许删除管理员
    if user.role == "admin":
        return {"message": "不能删除管理员账户"}

    await db.delete(user)
    await db.commit()
    return {"message": f"用户 '{user.username}' 已删除"}
