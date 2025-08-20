from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas import BlogSchema, BlogCreate, CommentCreate, CommentSchema
from typing import List, Optional
from datetime import datetime
from app.api.auth import get_current_user
from app.db import BlogStore, MemoryBlogStore
from app.models import User
import asyncio
from functools import lru_cache

router = APIRouter(tags=["blogs"])

# 按用户名分隔存储
user_blogs: dict[str, MemoryBlogStore] = {}

def get_store(user: User) -> MemoryBlogStore:
    return user_blogs.setdefault(user.username, MemoryBlogStore())

# helper: 根据 blog_id 查找对应用户的 store（优化版本）
@lru_cache(maxsize=256)
def _get_cached_blog_location(blog_id: int, cache_key: str):
    """缓存博客位置查找，cache_key用于缓存失效"""
    for username, store in user_blogs.items():
        if store.get_blog(blog_id):
            return username, store
    return None, None

def find_store_and_owner(blog_id: int):
    # 使用时间戳作为缓存键的一部分来控制缓存失效
    cache_key = f"{len(user_blogs)}_{sum(len(store.blogs) for store in user_blogs.values())}"
    return _get_cached_blog_location(blog_id, cache_key)

@router.get("/", response_model=List[BlogSchema], summary="获取所有博客")
async def read_blogs(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页数量")
):
    """获取博客列表，支持分页"""
    # 异步收集所有博客（模拟异步操作）
    all_blogs: List[BlogSchema] = []
    
    # 并发获取各用户的博客
    async def get_user_blogs(username: str, store: MemoryBlogStore):
        blogs = []
        for b in store.get_all():
            if b.is_public or username == current_user.username:
                blogs.append(b)
        return blogs
    
    # 使用异步任务收集博客
    tasks = [
        get_user_blogs(username, store) 
        for username, store in user_blogs.items()
    ]
    
    if tasks:
        results = await asyncio.gather(*tasks)
        for blog_list in results:
            all_blogs.extend(blog_list)
    
    # 按发布时间倒序排序
    all_blogs.sort(key=lambda x: x.created_at, reverse=True)
    
    # 分页处理
    start = (page - 1) * limit
    end = start + limit
    return all_blogs[start:end]

@router.post("/", response_model=BlogSchema, status_code=201, summary="创建博客")
async def create_blog(blog: BlogCreate, current_user: User = Depends(get_current_user)):
    store = get_store(current_user)
    
    # 异步获取下一个ID
    existing = store.get_all()
    next_id = max((b.id for b in existing), default=0) + 1
    
    new_blog = BlogSchema(
        id=next_id,
        title=blog.title,
        content=blog.content,
        author=current_user.username,
        created_at=datetime.utcnow(),
        is_public=blog.is_public
    )
    
    # 清除相关缓存
    _get_cached_blog_location.cache_clear()
    
    return store.create_blog(new_blog)

@router.get("/{blog_id}", response_model=BlogSchema, summary="获取单个博客")
async def read_blog(blog_id: int, current_user: User = Depends(get_current_user)):
    # 优先从当前用户的store查找
    user_store = get_store(current_user)
    blog = user_store.get_blog(blog_id)
    
    if not blog:
        # 如果在当前用户store中找不到，再查找其他用户
        owner, store = find_store_and_owner(blog_id)
        if store:
            blog = store.get_blog(blog_id)
            # 检查权限
            if not blog.is_public and owner != current_user.username:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "无权限访问")
    
    if not blog:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    
    return blog

@router.put("/{blog_id}", response_model=BlogSchema, summary="更新博客")
async def update_blog(blog_id: int, new_blog: BlogCreate, current_user: User = Depends(get_current_user)):
    store = get_store(current_user)
    existing = store.get_blog(blog_id)
    if not existing:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    
    # 生成更新的 BlogSchema，保留 author 和 created_at，并更新公开状态
    updated = BlogSchema(
        id=blog_id,
        title=new_blog.title,
        content=new_blog.content,
        author=current_user.username,
        created_at=existing.created_at,
        is_public=new_blog.is_public
    )
    
    # 清除缓存
    _get_cached_blog_location.cache_clear()
    
    return store.update_blog(blog_id, updated)

@router.delete("/{blog_id}", status_code=204, summary="删除博客")
async def delete_blog(blog_id: int, current_user: User = Depends(get_current_user)):
    store = get_store(current_user)
    if not store.get_blog(blog_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    
    store.delete_blog(blog_id)
    
    # 清除缓存
    _get_cached_blog_location.cache_clear()

# 点赞博客
@router.post("/{blog_id}/like", summary="点赞博客")
async def like_blog(blog_id: int, current_user: User = Depends(get_current_user)):
    owner, store = find_store_and_owner(blog_id)
    if not store:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    
    blog = store.get_blog(blog_id)
    if not blog.is_public and owner != current_user.username:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权限")
    
    try:
        likes = store.like_blog(blog_id, current_user.username)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    
    return {"likes": likes}

# 添加评论
@router.post("/{blog_id}/comments", response_model=CommentSchema, summary="添加评论")
async def add_comment(blog_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user)):
    owner, store = find_store_and_owner(blog_id)
    if not store:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    
    blog = store.get_blog(blog_id)
    if not blog.is_public and owner != current_user.username:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权限")
    
    return store.add_comment(blog_id, current_user.username, comment.content)

# 获取评论列表
@router.get("/{blog_id}/comments", response_model=List[CommentSchema], summary="获取评论")
async def get_comments(
    blog_id: int, 
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量")
):
    """获取评论列表，支持分页"""
    owner, store = find_store_and_owner(blog_id)
    if not store:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "博客未找到")
    
    blog = store.get_blog(blog_id)
    if not blog.is_public and owner != current_user.username:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权限")
    
    comments = store.get_comments(blog_id)
    
    # 分页处理
    start = (page - 1) * limit
    end = start + limit
    return comments[start:end]