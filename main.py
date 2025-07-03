import os
from dotenv import load_dotenv
import subprocess  # 新增：用于静默子进程输出
import logging
import requests  # 用于获取已存在 ngrok 隧道
from fastapi import FastAPI
from contextlib import asynccontextmanager
from pyngrok import ngrok, conf as pyngrok_conf
from pyngrok.conf import PyngrokConfig  # pyngrok 配置类
from subprocess import Popen as _Popen

# 定义自定义 Popen，用于屏蔽 ngrok 进程所有输出
class NgrokPopen(_Popen):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('stdout', subprocess.DEVNULL)
        kwargs.setdefault('stderr', subprocess.DEVNULL)
        super().__init__(*args, **kwargs)

# 屏蔽 pyngrok 和二进制日志输出
logging.getLogger("pyngrok").setLevel(logging.ERROR)
logging.getLogger("pyngrok.ngrok").setLevel(logging.ERROR)

def get_existing_tunnel_url(port: int):
    """通过 ngrok 本地 API 获取已存在隧道的公网 URL"""
    try:
        resp = requests.get(f"http://127.0.0.1:4040/api/tunnels")
        data = resp.json()
        for t in data.get("tunnels", []):
            if f"{port}" in t.get("config", {}).get("addr", ""):
                return t.get("public_url")
    except Exception:
        return None
    return None

# 1. 启动前先删除数据库文件
db_path = os.path.join(os.path.dirname(__file__), "app", "data.db")
if os.path.exists(db_path):
    os.remove(db_path)

load_dotenv()  # 加载根目录 .env 文件中的配置
from fastapi.middleware.cors import CORSMiddleware
from app.api import blog, auth, dino_game, admin
from fastapi.staticfiles import StaticFiles
from app.core.config import NGROK_AUTH_TOKEN, TUNNEL_PORT
from app.core.database import Base, engine
from fastapi.responses import RedirectResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Debug: NGROK_AUTH_TOKEN:", repr(NGROK_AUTH_TOKEN))
    # 尝试启动新 ngrok 隧道，若受限则获取现有隧道 URL
    public_url = None
    try:
        ngrok.kill()  # 终止旧会话，可能无效则忽略
    except:
        pass
    try:
        if NGROK_AUTH_TOKEN:
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        public_url = ngrok.connect(
            TUNNEL_PORT,
            pyngrok_config=PyngrokConfig(auth_token=NGROK_AUTH_TOKEN, web_addr=False, no_log=True, subprocess_kwargs={"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL})
        ).public_url
    except Exception:
        # 當 ngrok session 限制时，尝试从本地 API 获取已存在隧道
        public_url = get_existing_tunnel_url(TUNNEL_PORT)
    if public_url:
        print(f"🔗 Public URL: {public_url}")
    else:
        print("❌ 无法获取 ngrok 隧道 URL")
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blog.router, prefix="/blogs")
app.include_router(auth.router, prefix="/auth")
app.include_router(dino_game.router, prefix="/dino")
app.include_router(admin.router, prefix="/admin")

@app.get("/", include_in_schema=False)
def root():
    # 根路由重定向到前端首页
    return RedirectResponse(url="/static/pages/index.html")

# 2. 再创建表
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # 直接用 Python 运行时，自动使用同一端口启动服务
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=TUNNEL_PORT)