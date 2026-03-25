from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from models.user import User
from repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository, secret_key: str = "stdo-secret-key-change-in-production",
                 algorithm: str = "HS256"):
        self._user_repo = user_repo
        self._secret = secret_key
        self._algorithm = algorithm
        self._pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, plain: str) -> str:
        return self._pwd_ctx.hash(plain)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return self._pwd_ctx.verify(plain, hashed)

    def create_access_token(self, user: User, expires_minutes: int = 30) -> str:
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def create_refresh_token(self, user: User, expires_days: int = 7) -> str:
        payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=expires_days),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError:
            return None

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self._user_repo.get_by_username(username)
        if not user or not user.is_active:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def get_user_from_token(self, token: str) -> Optional[User]:
        payload = self.decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        user_id = int(payload["sub"])
        user = self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        return user

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        payload = self.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        user_id = int(payload["sub"])
        user = self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        return self.create_access_token(user)

    def register(self, username: str, email: str, password: str,
                 full_name: str, role: str = "engineer") -> User:
        if self._user_repo.get_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        if self._user_repo.get_by_email(email):
            raise ValueError(f"Email '{email}' already exists")
        hashed = self.hash_password(password)
        return self._user_repo.create(username, email, hashed, full_name, role)
