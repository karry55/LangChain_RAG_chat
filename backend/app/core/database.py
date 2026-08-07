"""数据库连接管理 — 含性能优化配置"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from loguru import logger
from .config import get_settings

settings = get_settings()

# 根据数据库类型调整连接池大小
is_sqlite = "sqlite" in settings.database_url
pool_size = 20 if not is_sqlite else 10  # SQLite 连接池不宜过大
max_overflow = 20

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_pre_ping=True,          # 连接前检查可用性
    pool_recycle=3600,           # 1 小时回收连接
    connect_args={
        # SQLite 优化参数
        "check_same_thread": False,  # FastAPI 多线程安全
    } if is_sqlite else {},
)

if is_sqlite:
    # === SQLite WAL 模式 + 性能优化 ===
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """每次 SQLite 连接建立时应用性能优化 PRAGMA"""
        cursor = dbapi_connection.cursor()
        # WAL 模式：写操作不阻塞读操作，单写多读模型
        cursor.execute("PRAGMA journal_mode=WAL;")
        # 同步模式 NORMAL：崩溃安全但更快（WAL 模式下已足够安全）
        cursor.execute("PRAGMA synchronous=NORMAL;")
        # 锁等待超时：写锁冲突时等待 5 秒而非立即失败
        cursor.execute("PRAGMA busy_timeout=5000;")
        # 缓存大小：增大到 64MB（默认仅 2MB）
        cursor.execute("PRAGMA cache_size=-64000;")
        # 内存映射 I/O：大文件读取更快
        cursor.execute("PRAGMA mmap_size=268435456;")  # 256MB
        # 临时文件存内存而非磁盘
        cursor.execute("PRAGMA temp_store=MEMORY;")
        # 外键约束（数据完整性）
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
        logger.debug("SQLite pragma applied: WAL + NORMAL sync + 5s busy_timeout")

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入：获取数据库会话

    SQLite WAL 模式 (journal_mode=WAL) 已支持写不阻塞读。
    busy_timeout=5000ms 在极端情况下提供合理的等待时间。
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表已初始化 (SQLite WAL 模式)")
