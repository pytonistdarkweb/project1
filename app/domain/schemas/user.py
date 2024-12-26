from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr = Field(..., description="Email address must be valid")

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserResponse):
    password_hash: str

    model_config = ConfigDict(from_attributes=True)