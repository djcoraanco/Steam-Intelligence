from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, EmailStr, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    roles: List[str]
    user_id: str
    email: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    roles: List[str] = []


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None
    role: str = "viewer"  # owner, admin, analyst, viewer


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    display_name: Optional[str] = None
    is_active: bool
    roles: List[str] = []
    created_at: datetime
    last_login_at: Optional[datetime] = None
