from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=1000)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Username must be alphanumeric with underscores."""
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('Username must be alphanumeric with underscores')
        return v


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=1000)
    full_name: str = Field(..., min_length=2, max_length=200)
    role: str = Field("engineer", max_length=50)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Username must be alphanumeric with underscores."""
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('Username must be alphanumeric with underscores')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Password must contain letters and numbers."""
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_letter and has_digit):
            raise ValueError('Password must contain letters and numbers')
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=1000)
