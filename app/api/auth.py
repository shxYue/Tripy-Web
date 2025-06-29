from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.schemas import UserCreate, Token, BlogSchema
from typing import Dict

router = APIRouter()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# 内存用户表
fake_users: Dict[str, Dict] = {
    "admin": {"username": "admin", "password": "password", "id": 1}
}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=Token, summary="用户注册")
def register(user: UserCreate):
    if user.username in fake_users:
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_id = max(u["id"] for u in fake_users.values()) + 1
    fake_users[user.username] = {
        "username": user.username,
        "password": user.password,
        "id": new_id
    }
    # 注册完成后直接签发 token
    token = create_token({"sub": user.username, "user_id": new_id})
    return {"access_token": token, "token_type": "bearer"}