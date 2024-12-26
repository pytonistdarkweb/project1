from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    translations: Mapped[List["TaskTranslation"]] = relationship(
        back_populates="task", 
        cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship(back_populates="tasks")

    def with_translation(self, language: str) -> dict:
        """Возвращает задачу с переводом на указанный язык"""
        translation = next(
            (t for t in self.translations if t.language == language), 
            None
        )
        
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": translation.title if translation else self.title,
            "description": translation.description if translation else self.description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    class Config:
        from_attributes = True
