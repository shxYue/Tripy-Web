from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List

from app.api.auth import get_current_user, get_db
from app.models import User, DinoScore
from sqlalchemy.orm import Session
from app.schemas import ScoreSubmit, LeaderboardEntry

router = APIRouter(tags=["dino_game"])

# --------- 数据模型 ---------
class GameState(BaseModel):
    position: int = 0
    score: int = 0
    is_active: bool = False

# --------- 内存存储 ---------
# 按用户名分隔存储
game_states: Dict[str, GameState] = {}

def get_game(user: User) -> GameState:
    return game_states.setdefault(user.username, GameState(is_active=False))

# --------- 游戏 API ---------
@router.post("/start", response_model=GameState, summary="开始游戏")
def start_game(current_user: User = Depends(get_current_user)):
    gs = GameState(is_active=True)
    game_states[current_user.username] = gs
    return gs

@router.post("/forward", response_model=GameState, summary="前进一步")
def surf_forward(current_user: User = Depends(get_current_user)):
    gs = get_game(current_user)
    if not gs.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请先开始游戏")
    gs.position += 1
    gs.score += 10
    return gs

@router.get("/status", response_model=GameState, summary="获取游戏状态")
def surf_status(current_user: User = Depends(get_current_user)):
    gs = get_game(current_user)
    return gs

@router.post("/reset", response_model=GameState, summary="重置游戏")
def surf_reset(current_user: User = Depends(get_current_user)):
    gs = GameState()
    game_states[current_user.username] = gs
    return gs

# --------- 分数 API ---------
@router.post("/score", response_model=LeaderboardEntry, summary="提交分数并更新最高分")
def submit_score(payload: ScoreSubmit, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 查找或创建最高分记录
    record = db.query(DinoScore).filter(DinoScore.user_id == current_user.id).first()
    if not record:
        record = DinoScore(user_id=current_user.id, score=payload.score)
        db.add(record)
    elif payload.score > record.score:
        record.score = payload.score
    # 屏蔽低于最高分的提交
    db.commit()
    return LeaderboardEntry(username=current_user.username, score=record.score)

@router.get("/leaderboard", response_model=List[LeaderboardEntry], summary="获取排行榜")
def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    # 获取前 N 名最高分
    results = db.query(DinoScore, User).join(User, DinoScore.user_id == User.id)
    results = results.order_by(DinoScore.score.desc()).limit(limit).all()
    return [LeaderboardEntry(username=user.username, score=ds.score) for ds, user in results]