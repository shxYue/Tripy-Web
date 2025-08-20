from typing import List, Optional, Dict
from app.schemas import BlogSchema, CommentSchema   # 将 Pydantic 模型 BlogSchema 当作 Blog 引入
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models import User
from datetime import datetime
import functools
import time

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 简单的缓存装饰器
def cache_with_ttl(ttl_seconds: int = 300):
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 创建缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            current_time = time.time()
            
            # 检查缓存
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            # 清理过期缓存（简单实现）
            if len(cache) > 100:  # 防止缓存过大
                expired_keys = [
                    k for k, (_, ts) in cache.items() 
                    if current_time - ts >= ttl_seconds
                ]
                for k in expired_keys:
                    cache.pop(k, None)
            
            return result
        return wrapper
    return decorator

@cache_with_ttl(ttl_seconds=60)  # 缓存1分钟
def get_user(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str) -> User:
    user = User(
        username=username,
        hashed_password=pwd_ctx.hash(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

class BlogStore:
    def get_all(self) -> List[BlogSchema]:
        raise NotImplementedError()

    def create_blog(self, blog: BlogSchema) -> BlogSchema:
        raise NotImplementedError()

    def get_blog(self, blog_id: int) -> Optional[BlogSchema]:
        raise NotImplementedError()

    def update_blog(self, blog_id: int, new_blog: BlogSchema) -> BlogSchema:
        raise NotImplementedError()

    def delete_blog(self, blog_id: int) -> None:
        raise NotImplementedError()


class MemoryBlogStore(BlogStore):
    def __init__(self):
        self.blogs: Dict[int, BlogSchema] = {}  # 使用字典而非列表，O(1)查找
        self.blogs_list: List[BlogSchema] = []  # 保留列表用于排序
        self.next_comment_id: Dict[int, int] = {}  # 存储每个 blog 的下一个 comment id
        self.like_map: Dict[int, set[str]] = {}  # 存储每个 blog 被哪些用户点赞
        self._cache_dirty = True  # 缓存脏标记
        self._sorted_cache: List[BlogSchema] = []  # 排序缓存

    def _invalidate_cache(self):
        """标记缓存为脏"""
        self._cache_dirty = True

    def get_all(self) -> List[BlogSchema]:
        if self._cache_dirty:
            self._sorted_cache = sorted(
                self.blogs_list, 
                key=lambda x: x.created_at, 
                reverse=True
            )
            self._cache_dirty = False
        return self._sorted_cache.copy()

    def create_blog(self, blog: BlogSchema) -> BlogSchema:
        if blog.id in self.blogs:
            raise Exception("Blog with this id already exists")
        
        # 初始化 likes、comments、like_map
        blog.likes = 0
        blog.comments = []
        self.next_comment_id[blog.id] = 1
        self.like_map[blog.id] = set()
        
        self.blogs[blog.id] = blog
        self.blogs_list.append(blog)
        self._invalidate_cache()
        return blog

    def get_blog(self, blog_id: int) -> Optional[BlogSchema]:
        return self.blogs.get(blog_id)

    def update_blog(self, blog_id: int, new_blog: BlogSchema) -> BlogSchema:
        if blog_id not in self.blogs:
            raise Exception("Blog not found")
        
        # 更新字典
        self.blogs[blog_id] = new_blog
        
        # 更新列表
        for idx, blog in enumerate(self.blogs_list):
            if blog.id == blog_id:
                self.blogs_list[idx] = new_blog
                break
        
        self._invalidate_cache()
        return new_blog

    def delete_blog(self, blog_id: int) -> None:
        if blog_id not in self.blogs:
            raise Exception("Blog not found")
        
        # 删除相关数据
        del self.blogs[blog_id]
        self.next_comment_id.pop(blog_id, None)
        self.like_map.pop(blog_id, None)
        
        # 从列表中删除
        self.blogs_list = [b for b in self.blogs_list if b.id != blog_id]
        self._invalidate_cache()
    
    # 新增：点赞/取消点赞功能，每个用户可切换点赞状态
    def like_blog(self, blog_id: int, username: str) -> int:
        blog = self.get_blog(blog_id)
        if not blog:
            raise Exception("Blog not found")
        users = self.like_map.get(blog_id)
        if username in users:
            users.remove(username)
        else:
            users.add(username)
        blog.likes = len(users)
        self._invalidate_cache()  # 点赞数变化需要重新排序
        return blog.likes
    
    # 新增：添加评论
    def add_comment(self, blog_id: int, author: str, content: str) -> CommentSchema:
        blog = self.get_blog(blog_id)
        if not blog:
            raise Exception("Blog not found")
        cid = self.next_comment_id.get(blog_id, 1)
        comment = CommentSchema(id=cid, author=author, content=content, created_at=datetime.utcnow())
        blog.comments.append(comment)
        self.next_comment_id[blog_id] = cid + 1
        return comment
    
    # 新增：获取评论列表
    def get_comments(self, blog_id: int) -> List[CommentSchema]:
        blog = self.get_blog(blog_id)
        if not blog:
            raise Exception("Blog not found")
        return blog.comments.copy()  # 返回副本避免外部修改


# 默认使用内存实现
blog_store = MemoryBlogStore()