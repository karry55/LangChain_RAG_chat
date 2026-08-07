"""认证相关 Pydantic 模型"""
from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码 (6-50位)")
    email: str = Field(default="", max_length=100, description="邮箱 (选填)")


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=1, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码 (6-50位)")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserInfo(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
