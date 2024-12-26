from app.Infrastructure.repository.task_repository import TaskRepository
from app.application.translation_services import TranslationService
from app.domain.models.task import Task
from app.domain.value_objects.time_interval import TimeInterval
from typing import List, Optional
from fastapi import BackgroundTasks

class TaskService:
    def __init__(self, task_repo: TaskRepository, translation_service: TranslationService):
        self.task_repo = task_repo
        self.translation_service = translation_service

    async def create_task(
        self, 
        user_id: int, 
        title: str, 
        description: str, 
        start_time: str, 
        end_time: str,
        background_tasks: BackgroundTasks,
        auto_translate: bool = True
    ) -> Task:
        # Проверяем временной интервал
        time_interval = TimeInterval(start_time=start_time, end_time=end_time)
        time_interval.validate()
        
        # Создаем задачу
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time
        )
        created_task = await self.task_repo.create_task(task)
        
        # Если включен автоперевод, добавляем задачу на перевод в фоновые задачи
        if auto_translate:
            background_tasks.add_task(
                self.translation_service.translate_and_save_task,
                created_task.id
            )
            
        return created_task

    async def get_tasks(
        self, 
        user_id: int, 
        language: str = "ru"
    ) -> List[Task]:
        tasks = await self.task_repo.get_tasks_by_user(user_id)
        
        # Если запрошен английский язык, возвращаем с переводами
        if language == "en":
            return [task.with_english_translation() for task in tasks]
        return tasks

    async def update_task(
        self, 
        task_id: int, 
        background_tasks: BackgroundTasks,
        **kwargs
    ) -> Optional[Task]:
        updated_task = await self.task_repo.update_task(task_id, **kwargs)
        
        # Если обновили заголовок или описание, запускаем перевод
        if updated_task and ("title" in kwargs or "description" in kwargs):
            background_tasks.add_task(
                self.translation_service.translate_and_save_task,
                task_id
            )
            
        return updated_task

    async def delete_task(self, task_id: int) -> bool:
        return await self.task_repo.delete_task(task_id)
