from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class TranslationBase(BaseModel):
    language: str = Field(..., min_length=2, max_length=2, description="ISO 639-1 language code")
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    model_config = ConfigDict(from_attributes=True)


class TaskTranslationCreate(TranslationBase):
    task_id: int = Field(..., gt=0)


class TaskTranslationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TaskTranslationResponse(TranslationBase):
    id: int
    task_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)