from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import get_current_user
from core.service_locator import get_locator
from dto.auth import (
    LoginRequest, RegisterRequest, TokenResponse,
    RefreshRequest, UserResponse, UpdateProfileRequest,
)
from models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    loc = get_locator()
    user = loc.auth_service.authenticate(body.username, body.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return TokenResponse(
        access_token=loc.auth_service.create_access_token(user),
        refresh_token=loc.auth_service.create_refresh_token(user),
    )


@router.post("/register", response_model=UserResponse)
def register(body: RegisterRequest, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only admin can register users")
    loc = get_locator()
    try:
        user = loc.auth_service.register(
            body.username, body.email, body.password, body.full_name, body.role,
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return UserResponse(
        id=user.id, username=user.username, email=user.email,
        full_name=user.full_name, role=user.role, is_active=user.is_active,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest):
    loc = get_locator()
    new_access = loc.auth_service.refresh_access_token(body.refresh_token)
    if not new_access:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    return TokenResponse(
        access_token=new_access,
        refresh_token=body.refresh_token,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id, username=current_user.username,
        email=current_user.email, full_name=current_user.full_name,
        role=current_user.role, is_active=current_user.is_active,
    )


@router.put("/me", response_model=UserResponse)
def update_me(body: UpdateProfileRequest, current_user: User = Depends(get_current_user)):
    loc = get_locator()
    updates = {}
    if body.full_name:
        updates["full_name"] = body.full_name
    if body.email:
        updates["email"] = body.email
    if body.password:
        updates["password_hash"] = loc.auth_service.hash_password(body.password)
    user = loc.user_repo.update(current_user.id, **updates)
    return UserResponse(
        id=user.id, username=user.username, email=user.email,
        full_name=user.full_name, role=user.role, is_active=user.is_active,
    )
