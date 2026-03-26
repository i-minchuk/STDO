from __future__ import annotations
from fastapi import APIRouter, Depends
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User

router = APIRouter(prefix="/api/gamification", tags=["gamification"])

LEVEL_TITLES = {1: "Новичок", 2: "Уверенный", 3: "Профессионал", 4: "Эксперт", 5: "Лидер проекта"}
LEVEL_THRESHOLDS = [(0, 1), (100, 2), (250, 3), (500, 4), (1000, 5)]
BADGES = [
    {"id": "reliable", "name": "Надёжный", "desc": "SPI >= 1.0 на протяжении 5 задач подряд"},
    {"id": "speedster", "name": "Скоростной", "desc": "3 задачи закрыты раньше срока"},
    {"id": "quality", "name": "Качественный", "desc": "0 возвратов на доработку за 10 ревизий"},
    {"id": "teamplayer", "name": "Командный", "desc": "Участие в 3+ проектах одновременно"},
    {"id": "marathon", "name": "Марафонец", "desc": "50+ закрытых задач"},
]


def _get_level(score: int) -> tuple:
    level = 1
    for threshold, lvl in LEVEL_THRESHOLDS:
        if score >= threshold:
            level = lvl
    return level, LEVEL_TITLES.get(level, "Новичок")


@router.get("/leaderboard")
def leaderboard(current_user: User = Depends(get_current_user)):
    loc = get_locator()
    users = loc.user_repo.get_all(active_only=True)
    board = []
    for u in users:
        if u.role == "admin":
            continue
        score = 0  # In real app, aggregate from gamification_events
        level, title = _get_level(score)
        board.append({
            "user_id": u.id, "username": u.username, "full_name": u.full_name,
            "score": score, "level": level, "level_title": title,
            "badges_count": 0,
        })
    board.sort(key=lambda x: x["score"], reverse=True)
    for i, entry in enumerate(board):
        entry["rank"] = i + 1
    return board


@router.get("/me")
def my_profile(current_user: User = Depends(get_current_user)):
    score = 0
    level, title = _get_level(score)
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "score": score,
        "level": level,
        "level_title": title,
        "badges": [],
        "next_level_at": next((t for t, l in LEVEL_THRESHOLDS if t > score), None),
    }


@router.get("/badges")
def available_badges(current_user: User = Depends(get_current_user)):
    return BADGES
