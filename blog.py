from fastapi import APIRouter, HTTPException
from models import Blog
from typing import List
from db import blog_store

router = APIRouter()

# 获取所有博客
@router.get("/", response_model=List[Blog])
def read_blogs():
    return blog_store.get_all()

# 创建博客
@router.post("/", response_model=Blog)
def create_blog(blog: Blog):
    try:
        return blog_store.create_blog(blog)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 获取单个博客
@router.get("/{blog_id}", response_model=Blog)
def read_blog(blog_id: int):
    blog = blog_store.get_blog(blog_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

# 更新博客
@router.put("/{blog_id}", response_model=Blog)
def update_blog(blog_id: int, new_blog: Blog):
    try:
        return blog_store.update_blog(blog_id, new_blog)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# 删除博客
@router.delete("/{blog_id}")
def delete_blog(blog_id: int):
    try:
        blog_store.delete_blog(blog_id)
        return {"detail": "Blog deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))