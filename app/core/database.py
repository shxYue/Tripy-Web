from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from .config import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, DEBUG

# SQLite 性能优化配置
engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 20,  # 连接超时
    },
    poolclass=StaticPool,  # 使用静态连接池
    pool_pre_ping=True,  # 连接前检查有效性
    pool_recycle=3600,  # 每小时回收连接
    echo=DEBUG,  # 根据DEBUG设置决定是否输出SQL日志
    # SQLite特定优化
    execution_options={
        "isolation_level": "AUTOCOMMIT"  # 自动提交模式
    }
)

# 执行SQLite性能优化设置
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """设置SQLite性能优化参数"""
    cursor = dbapi_connection.cursor()
    # 性能优化设置
    cursor.execute("PRAGMA journal_mode=WAL")  # 使用WAL模式提高并发性能
    cursor.execute("PRAGMA synchronous=NORMAL")  # 正常同步模式
    cursor.execute("PRAGMA cache_size=10000")  # 增加缓存大小
    cursor.execute("PRAGMA temp_store=MEMORY")  # 临时存储在内存中
    cursor.execute("PRAGMA mmap_size=268435456")  # 使用内存映射（256MB）
    cursor.close()

SessionLocal = sessionmaker(
    bind=engine, 
    autoflush=False, 
    autocommit=False,
    expire_on_commit=False  # 避免在事务提交后对象过期
)
Base = declarative_base()