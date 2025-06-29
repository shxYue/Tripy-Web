from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import *
from app.schemas import *

router = APIRouter()

# 冲浪小游戏数据
class SurfGame(BaseModel):
    player: str
    position: int = 0
    score: int = 0
    is_active: bool = False

surf_games = {}

# 开始游戏
@router.post("/start")
def start_game(player: str):
    surf_games[player] = SurfGame(player=player, position=0, score=0, is_active=True)
    return {"msg": f"{player} 的冲浪游戏开始啦！", "state": surf_games[player]}

# 前进一步
@router.post("/forward")
def surf_forward(player: str):
    game = surf_games.get(player)
    if not game or not game.is_active:
        raise HTTPException(status_code=400, detail="请先开始游戏")
    game.position += 1
    game.score += 10
    return {"msg": f"{player} 冲浪前进到 {game.position}，得分 {game.score}", "state": game}

# 获取当前状态
@router.get("/status")
def surf_status(player: str):
    game = surf_games.get(player)
    if not game:
        raise HTTPException(status_code=404, detail="没有找到该玩家的游戏")
    return game

# 结束/重置游戏
@router.post("/reset")
def surf_reset(player: str):
    if player in surf_games:
        surf_games[player] = SurfGame(player=player)
        return {"msg": f"{player} 的游戏已重置", "state": surf_games[player]}
    else:
        raise HTTPException(status_code=404, detail="没有找到该玩家的游戏")