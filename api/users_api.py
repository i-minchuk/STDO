from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from core.auth import require_role
from core.service_locator import get_locator
from dto.auth import RegisterRequest, UserResponse
from models.user import User

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/")
def list_users(current_user: User = Depends(require_role("admin", "manager"))):
    loc = get_locator()
    users = loc.user_repo.get_all()
    return [
        UserResponse(
            id=u.id, username=u.username, email=u.email,
            full_name=u.full_name, role=u.role, is_active=u.is_active,
        )
        for u in users
    ]


@router.post("/", response_model=UserResponse)
def create_user(body: RegisterRequest, current_user: User = Depends(require_role("admin"))):
    loc = get_locator()
    try:
        user = loc.auth_service.register(
            body.username, body.email, body.password, body.full_name, body.role,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        # Ловим UniqueViolation от psycopg2
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(409, "Пользователь с таким именем или email уже существует")
        raise HTTPException(500, f"Ошибка сохранения: {e}")
    return UserResponse(
        id=user.id, username=user.username, email=user.email,
        full_name=user.full_name, role=user.role, is_active=user.is_active,
    )


@router.put("/{user_id}")
def update_user(user_id: int, body: RegisterRequest, current_user: User = Depends(require_role("admin"))):
    loc = get_locator()
    updates = {"full_name": body.full_name, "email": body.email, "role": body.role}
    if body.password:
        updates["password_hash"] = loc.auth_service.hash_password(body.password)
    user = loc.user_repo.update(user_id, **updates)
    if not user:
        raise HTTPException(404, "User not found")
    return UserResponse(
        id=user.id, username=user.username, email=user.email,
        full_name=user.full_name, role=user.role, is_active=user.is_active,
    )


@router.put("/{user_id}/deactivate")
def deactivate_user(user_id: int, current_user: User = Depends(require_role("admin"))):
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot deactivate yourself")
    loc = get_locator()
    loc.user_repo.deactivate(user_id)
    return {"ok": True}
