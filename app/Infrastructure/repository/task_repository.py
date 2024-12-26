from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List, Optional, Dict
from app.domain.models.task import Task
from app.domain.models.translation import TaskTranslation

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_tasks_by_user(self, user_id: int, language: str = None) -> List[Task]:
        query = select(Task).where(Task.user_id == user_id)
        if language:
            query = query.join(Task.translations).where(TaskTranslation.language == language)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_task_by_id(self, task_id: int) -> Optional[Task]:
        result = await self.session.execute(
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.translations))
        )
        return result.scalars().first()

    async def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        task = await self.session.get(Task, task_id)
        if not task:
            return None
        for key, value in kwargs.items():
            setattr(task, key, value)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update_translation(
        self, 
        task_id: int, 
        language: str,
        title: str,
        description: Optional[str] = None
    ) -> Optional[TaskTranslation]:
        # Получаем существующий перевод или создаем новый
        translation = await self.session.execute(
            select(TaskTranslation).where(
                TaskTranslation.task_id == task_id,
                TaskTranslation.language == language
            )
        )
        translation = translation.scalars().first()

        if translation:
            # Обновляем существующий перевод
            translation.title = title
            translation.description = description
        else:
            # Создаем новый перевод
            translation = TaskTranslation(
                task_id=task_id,
                language=language,
                title=title,
                description=description
            )
            self.session.add(translation)

        await self.session.commit()
        await self.session.refresh(translation)
        return translation

    async def delete_task(self, task_id: int) -> bool:
        task = await self.session.get(Task, task_id)
        if task:
            await self.session.delete(task)
            await self.session.commit()
            return True
        return False

    async def get_task_translations(
        self, 
        task_id: int, 
        language: Optional[str] = None
    ) -> List[TaskTranslation]:
        query = select(TaskTranslation).where(TaskTranslation.task_id == task_id)
        if language:
            query = query.where(TaskTranslation.language == language)
        result = await self.session.execute(query)
        return result.scalars().all()