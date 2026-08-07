"""压力测试前准备：批量创建测试用户 + 确认知识库就绪"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import async_session
from app.core.security import hash_password
from app.models.user import User
from sqlalchemy import select, func


TEST_USER_COUNT = 100
TEST_USER_PREFIX = "testuser"
TEST_PASSWORD = "test123456"


async def create_test_users():
    """批量创建测试用户"""
    async with async_session() as db:
        # 查现有测试用户数
        result = await db.execute(
            select(func.count(User.id)).where(
                User.username.like(f"{TEST_USER_PREFIX}%")
            )
        )
        existing = result.scalar() or 0

        need = TEST_USER_COUNT - existing
        if need <= 0:
            print(f"[OK] 已有 {existing} 个测试用户，无需创建")
            return

        print(f"[INFO] 创建 {need} 个测试用户...")
        for i in range(existing + 1, TEST_USER_COUNT + 1):
            username = f"{TEST_USER_PREFIX}{i:03d}"
            user = User(
                username=username,
                password_hash=hash_password(TEST_PASSWORD),
                email=f"{username}@test.com",
                role="user",
            )
            db.add(user)

        await db.commit()
        print(f"[OK] 创建完成！共 {TEST_USER_COUNT} 个测试用户")
        print(f"   用户名格式: {TEST_USER_PREFIX}001 ~ {TEST_USER_PREFIX}{TEST_USER_COUNT:03d}")
        print(f"   密码统一为: {TEST_PASSWORD}")


async def check_knowledge_base():
    """检查知识库是否有文档"""
    from app.models.knowledge import KnowledgeDocument
    from sqlalchemy import select, func

    async with async_session() as db:
        result = await db.execute(select(func.count(KnowledgeDocument.id)))
        count = result.scalar() or 0
        if count == 0:
            print("[WARN]  知识库为空！请先上传测试文档：")
            print("   POST http://localhost:8000/api/knowledge/upload")
            print("   使用 admin / 123456 登录后上传")
        else:
            result = await db.execute(
                select(func.count(KnowledgeDocument.id)).where(
                    KnowledgeDocument.status == "completed"
                )
            )
            completed = result.scalar() or 0
            print(f"[KB] 知识库文档: {count} 个 (已完成: {completed})")


async def main():
    print("=" * 50)
    print("  压力测试环境准备")
    print("=" * 50)
    print()
    await create_test_users()
    print()
    await check_knowledge_base()
    print()
    print("=" * 50)
    print("  准备完成！可以启动 Locust 进行压测：")
    print("  cd backend && locust -f tests/locustfile.py")
    print("  浏览器打开 http://localhost:8089")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
