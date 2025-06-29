from typing import List, Optional
from models import Blog

class BlogStore:
    def get_all(self) -> List[Blog]:
        raise NotImplementedError()

    def create_blog(self, blog: Blog) -> Blog:
        raise NotImplementedError()

    def get_blog(self, blog_id: int) -> Optional[Blog]:
        raise NotImplementedError()

    def update_blog(self, blog_id: int, new_blog: Blog) -> Blog:
        raise NotImplementedError()

    def delete_blog(self, blog_id: int) -> None:
        raise NotImplementedError()


class MemoryBlogStore(BlogStore):
    def __init__(self):
        self.blogs: List[Blog] = []

    def get_all(self) -> List[Blog]:
        return self.blogs

    def create_blog(self, blog: Blog) -> Blog:
        if any(b.id == blog.id for b in self.blogs):
            raise Exception("Blog with this id already exists")
        self.blogs.append(blog)
        return blog

    def get_blog(self, blog_id: int) -> Optional[Blog]:
        for blog in self.blogs:
            if blog.id == blog_id:
                return blog
        return None

    def update_blog(self, blog_id: int, new_blog: Blog) -> Blog:
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