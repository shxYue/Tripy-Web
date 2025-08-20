from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'data.db'}"

# 隧道配置
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "")
TUNNEL_PORT = int(os.getenv("TUNNEL_PORT", "8000"))
TUNNEL_MODE = os.getenv("TUNNEL_MODE", "")  # 隧道模式: 'ngrok', 'localtunnel' (或 'lt')，或空表示不启用
LOCALTUNNEL_SUBDOMAIN = os.getenv("LOCALTUNNEL_SUBDOMAIN", "")  # localtunnel 子域名，留空则随机

# 性能配置
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 缓存时间(秒)，默认5分钟
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "120"))  # 每分钟最大请求数
SLOW_REQUEST_THRESHOLD = float(os.getenv("SLOW_REQUEST_THRESHOLD", "0.5"))  # 慢请求阈值(秒)

# 数据库配置
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))  # 数据库连接池大小
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))  # 连接池溢出大小
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # 连接池超时时间

# 应用配置
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))

# 分页配置
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))