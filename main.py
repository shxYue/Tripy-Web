from fastapi import FastAPI
from blog import router as blog_router
from surf import router as surf_router

app = FastAPI()

# 注册各模块路由
app.include_router(blog_router, prefix="/blogs")
app.include_router(surf_router, prefix="/surf")