from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from blog import router as blog_router
from surf import router as surf_router
from fastapi.staticfiles import StaticFiles
# ...existing code...

app = FastAPI()

# 添加静态文件服务
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册各模块路由
app.include_router(blog_router, prefix="/blogs")
app.include_router(surf_router, prefix="/surf")