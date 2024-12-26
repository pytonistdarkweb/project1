from app.Infrastructure.repository.task_repository import TaskRepository
from app.Infrastructure.translation_client import TranslationClient
from typing import Optional, Tuple
from app.domain.models.task import Task

class TranslationService:
    def __init__(self, task_repo: TaskRepository, translation_client: TranslationClient):
        self.task_repo = task_repo
        self.translation_client = translation_client

    async def translate_task(self, task: Task) -> Tuple[str, Optional[str]]:
        # Переводим заголовок и описание
        title_en = await self.translation_client.translate_text(task.title)
        description_en = None
        if task.description:
            description_en = await self.translation_client.translate_text(task.description)
        
        # Сохраняем переводы в БД
        await self.task_repo.update_translation(
            task_id=task.id,
            title_en=title_en,
            description_en=description_en
        )
        
        return title_en, description_en

    async def translate_and_save_task(self, task_id: int) -> Optional[Task]:
        task = await self.task_repo.get_task_by_id(task_id)
        if not task:
            return None
            
        await self.translate_task(task)
        return task