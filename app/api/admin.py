from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import SessionLocal
from app.models import User, DinoScore
from app.schemas import UserOut, BlogSchema, ScoreSubmit, LeaderboardEntry
from app.api.auth import get_current_user, get_db
from app.api.blog import user_blogs

router = APIRouter(tags=["admin"])

ADMIN_USERNAME = "admin"      # 这里修改管理员账号
ADMIN_PASSWORD = "admin123"   # 这里修改管理员密码

class AdminLoginIn(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def admin_login(data: AdminLoginIn):
    if data.username == ADMIN_USERNAME and data.password == ADMIN_PASSWORD:
        return {"msg": "ok", "token": "admin-token"}
    raise HTTPException(401, "用户名或密码错误")

@router.get("/users", response_model=List[UserOut], summary="获取所有用户（仅 admin）")
def list_users(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("X-Admin-Token")
    if token != "admin-token":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="无权限")
    return db.query(User).all()

# --------- 博客管理 API ---------
@router.get("/blogs", response_model=List[BlogSchema], summary="获取所有用户博客（仅 admin）")
def list_blogs(request: Request):
    token = request.headers.get("X-Admin-Token")
    if token != "admin-token":
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    # 聚合所有用户的博客
    all_blogs: List[BlogSchema] = []
    for store in user_blogs.values():
        all_blogs.extend(store.get_all())
    return all_blogs

@router.put("/blogs/{blog_id}", response_model=BlogSchema, summary="更新博客内容（仅 admin）")
def update_blog(blog_id: int, blog: BlogSchema, request: Request):
    token = request.headers.get("X-Admin-Token")
    if token != "admin-token":
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    # 在所有用户存储中查找该博客并更新
    for store in user_blogs.values():
        existing = store.get_blog(blog_id)
        if existing:
            blog.id = blog_id
            return store.update_blog(blog_id, blog)
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="博客未找到")

# --------- 游戏分数管理 API ---------
@router.get("/scores", response_model=List[LeaderboardEntry], summary="获取所有用户最高分（仅 admin）")
def list_scores(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("X-Admin-Token")
    if token != "admin-token":
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    results = db.query(DinoScore, User).join(User, DinoScore.user_id == User.id).all()
    return [LeaderboardEntry(username=user.username, score=ds.score) for ds, user in results]

@router.put("/scores/{username}", response_model=LeaderboardEntry, summary="修改用户最高分（仅 admin）")
def update_score(username: str, payload: ScoreSubmit, request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("X-Admin-Token")
    if token != "admin-token":
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="用户不存在")
    record = db.query(DinoScore).filter(DinoScore.user_id == user.id).first()
    if not record:
        record = DinoScore(user_id=user.id, score=payload.score)
        db.add(record)
    else:
        record.score = payload.score
    db.commit()
    return LeaderboardEntry(username=username, score=record.score)