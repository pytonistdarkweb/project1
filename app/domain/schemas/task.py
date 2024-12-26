from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True


class TaskCreate(TaskBase):
    auto_translate: bool = Field(default=True, description="Automatically translate task")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskTranslation(BaseModel):
    language: str = Field(..., min_length=2, max_length=2)
    title: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    translations: List[TaskTranslation] = []

    class Config:
        from_attributes = True


class TaskDelete(BaseModel):
    task_id: int = Field(..., gt=0)

    class Config:
        from_attributes = True