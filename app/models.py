from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)

# 添加小恐龙游戏分数表，记录每个用户的最高分
class DinoScore(Base):
    __tablename__ = "dino_scores"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    score = Column(Integer, default=0)