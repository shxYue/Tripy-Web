from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        from_attributes = True

class BlogSchema(BaseModel):
    id: int
    title: str
    content: str
    author: str = ""

# 添加分数提交和排行榜输出模型
class ScoreSubmit(BaseModel):
    score: int

class LeaderboardEntry(BaseModel):
    username: str
    score: int