from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User

router = APIRouter(prefix="/api/gamification", tags=["gamification"])

LEVEL_TITLES = {1: "Новичок", 2: "Уверенный", 3: "Профессионал", 4: "Эксперт", 5: "Лидер проекта"}
LEVEL_THRESHOLDS = [(0, 1), (100, 2), (250, 3), (500, 4), (1000, 5)]

# Badge definitions with criteria
BADGE_DEFINITIONS = [
    {
        "id": "first_project",
        "name": "Первый проект",
        "desc": "Создание первого проекта",
        "criteria": {"event_type": "project_created", "min_count": 1}
    },
    {
        "id": "reliable",
        "name": "Надёжный",
        "desc": "SPI >= 1.0 на протяжении 5 задач подряд",
        "criteria": {"event_type": "task_completed_on_time", "min_count": 5}
    },
    {
        "id": "speedster",
        "name": "Скоростной",
        "desc": "3 задачи закрыты раньше срока",
        "criteria": {"event_type": "task_completed_early", "min_count": 3}
    },
    {
        "id": "quality",
        "name": "Качественный",
        "desc": "0 возвратов на доработку за 10 ревизий",
        "criteria": {"event_type": "revision_without_returns", "min_count": 10}
    },
    {
        "id": "teamplayer",
        "name": "Командный",
        "desc": "Участие в 3+ проектах одновременно",
        "criteria": {"event_type": "multi_project_participation", "min_count": 1}
    },
    {
        "id": "marathon",
        "name": "Марафонец",
        "desc": "50+ закрытых задач",
        "criteria": {"event_type": "task_completed_on_time", "min_count": 50}
    },
    {
        "id": "perfectionist",
        "name": "Перфекционист",
        "desc": "10 ревизий без замечаний",
        "criteria": {"event_type": "revision_without_remarks", "min_count": 10}
    },
    {
        "id": "innovator",
        "name": "Инноватор",
        "desc": "Создание 5 новых документов",
        "criteria": {"event_type": "document_created", "min_count": 5}
    },
    {
        "id": "reviewer",
        "name": "Рецензент",
        "desc": "Проверка 20 документов",
        "criteria": {"event_type": "document_reviewed", "min_count": 20}
    },
    {
        "id": "time_manager",
        "name": "Управленец временем",
        "desc": "Завершение 10 задач точно в срок",
        "criteria": {"event_type": "task_completed_on_time", "min_count": 10}
    },
    {
        "id": "vdr_master",
        "name": "Мастер VDR",
        "desc": "Успешное проведение 5 VDR сессий",
        "criteria": {"event_type": "vdr_completed", "min_count": 5}
    },
    {
        "id": "otk_expert",
        "name": "Эксперт ОТК",
        "desc": "Проведение 10 проверок ОТК",
        "criteria": {"event_type": "otk_completed", "min_count": 10}
    },
    {
        "id": "approver",
        "name": "Одобритель",
        "desc": "Одобрение 25 ревизий документов",
        "criteria": {"event_type": "revision_approved", "min_count": 25}
    },
    {
        "id": "crs_clean",
        "name": "Чистый CRS",
        "desc": "10 CRS проверок без замечаний",
        "criteria": {"event_type": "crs_remark_created", "min_count": 0, "max_count": 0}
    },
    {
        "id": "punctual",
        "name": "Пунктуальный",
        "desc": "20 задач без опозданий",
        "criteria": {"event_type": "task_completed_late", "min_count": 0, "max_count": 0}
    },
    {
        "id": "review_master",
        "name": "Мастер проверки",
        "desc": "15 своевременных проверок документов",
        "criteria": {"event_type": "review_completed_on_time", "min_count": 15}
    },
    {
        "id": "quality_reviewer",
        "name": "Качественный рецензент",
        "desc": "10 проверок документов без опозданий",
        "criteria": {"event_type": "review_completed_late", "min_count": 0, "max_count": 0}
    },
]


def _get_level(score: int) -> tuple:
    level = 1
    for threshold, lvl in LEVEL_THRESHOLDS:
        if score >= threshold:
            level = lvl
    return level, LEVEL_TITLES.get(level, "Новичок")


def award_gamification_with_badges(locator, user_id: int, event_type: str, points: int, project_id: Optional[int] = None, comment: Optional[str] = None):
    """Award gamification points and check for badge unlocks."""
    from typing import Optional
    
    # Apply combo multiplier
    try:
        combo_multiplier = locator.combo_achievement_repo.get_combo_multiplier(user_id, event_type)
        adjusted_points = int(points * combo_multiplier)
    except:
        adjusted_points = points
    
    locator.gamification_event_repo.insert(
        user_id=user_id,
        event_type=event_type,
        points_delta=adjusted_points,
        project_id=project_id,
        comment=comment,
    )
    
    # Update combo achievement for tracking streaks
    try:
        locator.combo_achievement_repo.increment_combo(user_id, event_type)
    except:
        pass
    
    _check_and_award_badges(user_id, event_type, locator)


def _check_and_award_badges(user_id: int, event_type: str, locator):
    """Check if user qualifies for any badges based on event and award them."""
    for badge_def in BADGE_DEFINITIONS:
        criteria = badge_def["criteria"]
        if criteria["event_type"] == event_type or ("max_count" in criteria and criteria["event_type"] == event_type):
            # Count events of this type for user
            count = locator.gamification_event_repo.get_user_event_count(user_id, event_type)
            
            # Check criteria
            min_count = criteria.get("min_count", 0)
            max_count = criteria.get("max_count")
            
            qualifies = False
            if max_count is not None:
                # For badges that require MAX count (like 0 CRS remarks)
                qualifies = count <= max_count
            else:
                # For badges that require MIN count
                qualifies = count >= min_count
            
            if qualifies:
                # Award badge if not already awarded
                badge = locator.gamification_badge_repo.award_badge_if_not_exists(
                    user_id=user_id,
                    badge_id=badge_def["id"],
                    name=badge_def["name"],
                    description=badge_def["desc"],
                    metadata={"event_count": count, "awarded_for": event_type}
                )
                
                # Create notification if badge was awarded
                if badge:
                    locator.notification_repo.insert(
                        user_id=user_id,
                        type="badge_awarded",
                        title=f"🏆 Получен бейдж: {badge.name}",
                        message=f"Поздравляем! Вы получили бейдж '{badge.name}' за {badge_def['desc'].lower()}",
                        metadata={"badge_id": badge.badge_id, "badge_name": badge.name}
                    )


@router.get("/leaderboard")
def leaderboard(current_user: User = Depends(get_current_user)):
    loc = get_locator()
    users = loc.user_repo.get_all(active_only=True)
    board = []
    for u in users:
        if u.role == "admin":
            continue
        score = loc.gamification_event_repo.get_user_score(u.id)
        level, title = _get_level(score)
        badges = loc.gamification_badge_repo.get_user_badges(u.id)
        board.append({
            "user_id": u.id, "username": u.username, "full_name": u.full_name,
            "score": score, "level": level, "level_title": title,
            "badges_count": len(badges),
            "badges": [{"id": b.badge_id, "name": b.name} for b in badges],
        })
    board.sort(key=lambda x: x["score"], reverse=True)
    for i, entry in enumerate(board):
        entry["rank"] = i + 1
    return board


@router.get("/me")
def my_profile(current_user: User = Depends(get_current_user)):
    loc = get_locator()
    score = loc.gamification_event_repo.get_user_score(current_user.id)
    level, title = _get_level(score)
    events = loc.gamification_event_repo.get_user_events(current_user.id, limit=10)
    badges = loc.gamification_badge_repo.get_user_badges(current_user.id)
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "score": score,
        "level": level,
        "level_title": title,
        "badges": [
            {
                "id": b.badge_id,
                "name": b.name,
                "description": b.description,
                "awarded_at": b.awarded_at.isoformat(),
            }
            for b in badges
        ],
        "next_level_at": next((t for t, l in LEVEL_THRESHOLDS if t > score), None),
        "recent_events": [
            {
                "event_type": e.event_type,
                "points_delta": e.points_delta,
                "created_at": e.created_at.isoformat(),
                "comment": e.comment,
            }
            for e in events
        ],
    }


@router.get("/badges")
def available_badges(current_user: User = Depends(get_current_user)):
    return BADGE_DEFINITIONS


@router.get("/notifications")
def get_notifications(current_user: User = Depends(get_current_user)):
    loc = get_locator()
    notifications = loc.notification_repo.get_user_notifications(current_user.id)
    return [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]


@router.put("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, current_user: User = Depends(get_current_user)):
    loc = get_locator()
    success = loc.notification_repo.mark_as_read(notification_id, current_user.id)
    if not success:
        raise HTTPException(404, "Notification not found")
    return {"ok": True}


@router.get("/notifications/unread-count")
def get_unread_count(current_user: User = Depends(get_current_user)):
    loc = get_locator()
    count = loc.notification_repo.get_unread_count(current_user.id)
    return {"count": count}


@router.get("/daily-quests")
def get_daily_quests(current_user: User = Depends(get_current_user)):
    from datetime import date
    loc = get_locator()
    quests = loc.daily_quest_repo.get_user_daily_quests(current_user.id, date.today())
    if not quests:
        quests = loc.daily_quest_repo.create_daily_quests_for_user(current_user.id, date.today())

    return [
        {
            "id": q.id,
            "quest_type": q.quest_type,
            "title": q.title,
            "description": q.description,
            "target_count": q.target_count,
            "current_count": q.current_count,
            "reward_points": q.reward_points,
            "reward_xp": q.reward_xp,
            "is_completed": q.is_completed,
            "completed_at": q.completed_at.isoformat() if q.completed_at else None,
        }
        for q in quests
    ]


@router.post("/daily-quests/{quest_type}/progress")
def update_quest_progress(quest_type: str, current_user: User = Depends(get_current_user)):
    from datetime import date
    loc = get_locator()
    quest = loc.daily_quest_repo.update_quest_progress(current_user.id, quest_type, date.today())

    if not quest:
        raise HTTPException(404, "Quest not found")

    # Award points if quest was just completed
    if quest.is_completed and quest.completed_at:
        award_gamification_with_badges(
            loc, current_user.id, "daily_quest_completed",
            quest.reward_points, comment=f"Выполнено ежедневное задание: {quest.title}"
        )

    return {
        "id": quest.id,
        "quest_type": quest.quest_type,
        "title": quest.title,
        "description": quest.description,
        "target_count": quest.target_count,
        "current_count": quest.current_count,
        "reward_points": quest.reward_points,
        "reward_xp": quest.reward_xp,
        "is_completed": quest.is_completed,
        "completed_at": quest.completed_at.isoformat() if quest.completed_at else None,
    }
