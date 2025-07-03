from typing import List, Optional
from app.schemas import BlogSchema   # 将 Pydantic 模型 BlogSchema 当作 Blog 引入
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models import User

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        self.blogs: List[BlogSchema] = []

    def get_all(self) -> List[BlogSchema]:
        return self.blogs

    def create_blog(self, blog: BlogSchema) -> BlogSchema:
        if any(b.id == blog.id for b in self.blogs):
            raise Exception("Blog with this id already exists")
        self.blogs.append(blog)
        return blog

    def get_blog(self, blog_id: int) -> Optional[BlogSchema]:
        for blog in self.blogs:
            if blog.id == blog_id:
                return blog
        return None

    def update_blog(self, blog_id: int, new_blog: BlogSchema) -> BlogSchema:
        for idx, blog in enumerate(self.blogs):
            if blog.id == blog_id:
                self.blogs[idx] = new_blog
                return new_blog
        raise Exception("Blog not found")

    def delete_blog(self, blog_id: int) -> None:
        for idx, blog in enumerate(self.blogs):
            if blog.id == blog_id:
                self.blogs.pop(idx)
                return
        raise Exception("Blog not found")


# 默认使用内存实现
blog_store = MemoryBlogStore()