from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas import BlogSchema
from app.api.auth import get_current_user
from app.db import BlogStore, MemoryBlogStore
from app.models import User

router = APIRouter(tags=["blogs"])

# 按用户名分隔存储
user_blogs: dict[str, MemoryBlogStore] = {}

def get_store(user: User) -> MemoryBlogStore:
    return user_blogs.setdefault(user.username, MemoryBlogStore())

@router.get("/", response_model=List[BlogSchema], summary="获取所有博客")
def read_blogs(current_user: User = Depends(get_current_user)):
    return get_store(current_user).get_all()

@router.post("/", response_model=BlogSchema, status_code=201, summary="创建博客")
def create_blog(blog: BlogSchema, current_user: User = Depends(get_current_user)):
    store = get_store(current_user)
    # 避免重复 ID
    if store.get_blog(blog.id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "ID 已存在")
    return store.create_blog(blog)

@router.get("/{blog_id}", response_model=BlogSchema, summary="获取单个博客")
def read_blog(blog_id: int, current_user: User = Depends(get_current_user)):
    b = get_store(current_user).get_blog(blog_id)
    if not b:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    return b

@router.put("/{blog_id}", response_model=BlogSchema, summary="更新博客")
def update_blog(blog_id: int, new_blog: BlogSchema, current_user: User = Depends(get_current_user)):
    store = get_store(current_user)
    # 先检查是否存在
    if not store.get_blog(blog_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    # 保证路径 ID 与 body ID 一致
    new_blog.id = blog_id
    return store.update_blog(blog_id, new_blog)

@router.delete("/{blog_id}", status_code=204, summary="删除博客")
def delete_blog(blog_id: int, current_user: User = Depends(get_current_user)):
    store = get_store(current_user)
    if not store.get_blog(blog_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    store.delete_blog(blog_id)
    # 返回 204 时不需要 Body