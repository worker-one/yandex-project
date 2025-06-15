from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=3, max_length=50)
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserRead(UserBase):
    id: int
    is_superuser: bool
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    yandex_oauth_access_token: Optional[str] = None
    yandex_oauth_refresh_token: Optional[str] = None
    yandex_oauth_token_expires_at: Optional[datetime] = None
    yandex_id: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    avatar_url: Optional[str] = None
    # Email cannot be updated directly through this schema

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

# --- Login Schemas ---
class LoginRequest(BaseModel):
    email: EmailStr = None
    username: Optional[str] = None
    password: str
    
class TokenPayload(BaseModel):
    sub: int
    exp: datetime
    # Add other claims if needed
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# --- Yandex OAuth Schemas ---
class YandexOAuthCode(BaseModel):
    code: str

class YandexCallbackResponseData(BaseModel):
    access_token: str
    refresh_token: str
    user_profile: UserRead # Use your existing UserRead schema