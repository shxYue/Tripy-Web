from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import BlogSchema
from app.db import blog_store         # 改为绝对导入

router = APIRouter(prefix="/blogs", tags=["blogs"])

@router.get("/", response_model=List[BlogSchema], summary="获取所有博客")
def read_blogs():
    return blog_store.get_all()

@router.post("/", response_model=BlogSchema, status_code=201, summary="创建博客")
def create_blog(blog: BlogSchema):
    # 避免重复 ID
    if blog_store.get_blog(blog.id):
        raise HTTPException(status_code=400, detail="ID 已存在，无法创建")
    return blog_store.create_blog(blog)

@router.get("/{blog_id}", response_model=BlogSchema, summary="获取单个博客")
def read_blog(blog_id: int):
    b = blog_store.get_blog(blog_id)
    if not b:
        raise HTTPException(status_code=404, detail="博客未找到")
    return b

@router.put("/{blog_id}", response_model=BlogSchema, summary="更新博客")
def update_blog(blog_id: int, new_blog: BlogSchema):
    # 先检查是否存在
    existing = blog_store.get_blog(blog_id)
    if not existing:
        raise HTTPException(status_code=404, detail="博客未找到")
    # 保证路径 ID 与 body ID 一致
    new_blog.id = blog_id
    return blog_store.update_blog(blog_id, new_blog)

@router.delete("/{blog_id}", status_code=204, summary="删除博客")
def delete_blog(blog_id: int):
    if not blog_store.get_blog(blog_id):
        raise HTTPException(status_code=404, detail="博客未找到")
    blog_store.delete_blog(blog_id)
    # 返回 204 时不需要 Body