import os
import subprocess  # 用于静默子进程输出
import logging
import requests  # 用于获取已存在隧道
from dotenv import load_dotenv
# 加载 .env 配置，override=True 确保 .env 变量每次覆盖
load_dotenv(override=True)

import asyncio
try:
    from asyncio import WindowsSelectorEventLoopPolicy
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import time

from app.core.config import NGROK_AUTH_TOKEN, TUNNEL_PORT, TUNNEL_MODE
from app.core.tunnel import setup_tunnel
from app.core.database import Base, engine
from app.middleware.performance import PerformanceMiddleware, RequestLimitMiddleware

from app.api import blog, auth, dino_game, admin, user
from app.api.tunnel import router as tunnel_router  # localtunnel 代理
from app.core.config import TUNNEL_MODE  # 隧道模式

# 屏蔽 pyngrok 和二进制日志输出
logging.getLogger("pyngrok").setLevel(logging.ERROR)
logging.getLogger("pyngrok.ngrok").setLevel(logging.ERROR)

PUBLIC_URL: str = ""  # 存储隧道地址

# 优化的异步 Lifespan manager for tunnels
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 应用启动中...")
    start_time = time.time()
    
    # 异步初始化数据库
    await asyncio.get_event_loop().run_in_executor(None, init_database)
    
    # 如果启用隧道，异步设置隧道（不阻塞启动）
    if TUNNEL_MODE.lower() in ("ngrok", "localtunnel", "lt"):
        asyncio.create_task(setup_tunnel_async())
    
    startup_time = time.time() - start_time
    print(f"✅ 应用启动完成，耗时: {startup_time:.2f}s")
    
    yield
    
    print("🔄 应用关闭中...")

def init_database():
    """初始化数据库（仅在需要时创建表）"""
    # 不再强制删除数据库文件，让 SQLite 自然处理
    # 只创建不存在的表
    Base.metadata.create_all(bind=engine)
    print("📊 数据库初始化完成")

async def setup_tunnel_async():
    """异步设置隧道，不阻塞应用启动"""
    try:
        loop = asyncio.get_event_loop()
        public_url, _ = await loop.run_in_executor(None, setup_tunnel, TUNNEL_PORT)
        if public_url:
            print(f"🔗 公网 URL: {public_url}")
            global PUBLIC_URL
            PUBLIC_URL = public_url
        else:
            print("❌ 未启用或无法获取隧道 URL")
    except Exception as e:
        print(f"⚠️ 隧道设置失败: {e}")

# 仅在启用隧道模式时使用 lifespan
if TUNNEL_MODE.lower() in ("ngrok", "localtunnel", "lt"):
    app = FastAPI(lifespan=lifespan, title="Tripy-Web API", version="1.0.0")
else:
    app = FastAPI(title="Tripy-Web API", version="1.0.0")
    # 非隧道模式下也需要初始化数据库
    @asynccontextmanager
    async def simple_lifespan(app: FastAPI):
        await asyncio.get_event_loop().run_in_executor(None, init_database)
        yield
    app = FastAPI(lifespan=simple_lifespan, title="Tripy-Web API", version="1.0.0")

# 添加性能优化中间件
app.add_middleware(PerformanceMiddleware, slow_request_threshold=0.5)  # 记录超过0.5秒的慢请求
app.add_middleware(RequestLimitMiddleware, max_requests_per_minute=120)  # 限制每分钟120次请求
app.add_middleware(GZipMiddleware, minimum_size=1000)  # 启用Gzip压缩

# 优化静态文件服务
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(blog.router, prefix="/blogs")
app.include_router(auth.router, prefix="/auth")
app.include_router(dino_game.router, prefix="/dino")
app.include_router(admin.router, prefix="/admin")
app.include_router(user.router, prefix="/users")  # 注册用户管理路由

if TUNNEL_MODE.lower() in ("localtunnel", "lt"):
    app.include_router(tunnel_router, prefix="/tunnel", tags=["tunnel"])  # 代理 localtunnel 请求

@app.get("/", include_in_schema=False)
async def root():
    # 根路由重定向到前端首页
    return RedirectResponse(url="/static/pages/index.html")

# 健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "tunnel_url": PUBLIC_URL or None,
        "tunnel_mode": TUNNEL_MODE
    }

if __name__ == "__main__":
    # 直接用 Python 运行时的优化启动
    print("🚀 启动 Tripy-Web 服务...")
    
    # 非异步模式下的隧道设置（仅在直接运行时）
    if TUNNEL_MODE.lower() in ("ngrok", "localtunnel", "lt"):
        print("🔗 设置隧道...")
        try:
            public_url, _ = setup_tunnel(TUNNEL_PORT)
            if public_url:
                print(f"🔗 公网 URL: {public_url}")
                PUBLIC_URL = public_url
            else:
                print("❌ 未启用或无法获取隧道 URL")
        except Exception as e:
            print(f"⚠️ 隧道设置失败: {e}")
    
    # 初始化数据库
    init_database()
    
    # 启动 FastAPI 服务（生产环境配置）
    import uvicorn
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=TUNNEL_PORT,
        # 性能优化配置
        workers=1,  # 单进程模式（适合开发环境）
        loop="asyncio",  # 使用asyncio事件循环
        http="httptools",  # 使用httptools提高HTTP解析性能
        access_log=False  # 关闭访问日志提高性能
    )