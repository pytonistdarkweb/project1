from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from app.domain.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.application.task_services import TaskService
from app.application.translation_services import TranslationService
from app.Infrastructure.repository.task_repository import TaskRepository
from app.Infrastructure.translation_client import TranslationClient
from app.Infrastructure.database import AsyncSessionLocal
from app.api.deps import get_current_user
from app.domain.models.user import User

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])

@tasks_router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        task_repo = TaskRepository(session)
        translation_client = TranslationClient()
        translation_service = TranslationService(task_repo, translation_client)
        task_service = TaskService(task_repo, translation_service)
        
        return await task_service.create_task(
            user_id=current_user.id,
            title=task_data.title,
            description=task_data.description,
            start_time=task_data.start_time,
            end_time=task_data.end_time,
            background_tasks=background_tasks,
            auto_translate=task_data.auto_translate
        )

@tasks_router.get("", response_model=List[TaskResponse])
async def get_tasks(
    language: str = "ru",
    current_user: User = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        task_repo = TaskRepository(session)
        translation_service = TranslationService(task_repo, TranslationClient())
        task_service = TaskService(task_repo, translation_service)
        
        return await task_service.get_tasks(current_user.id, language)

@tasks_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        task_repo = TaskRepository(session)
        task = await task_repo.get_task_by_id(task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

@tasks_router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        task_repo = TaskRepository(session)
        translation_service = TranslationService(task_repo, TranslationClient())
        task_service = TaskService(task_repo, translation_service)
        
        task = await task_repo.get_task_by_id(task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")
            
        return await task_service.update_task(
            task_id=task_id,
            background_tasks=background_tasks,
            **task_data.model_dump(exclude_unset=True)
        )

@tasks_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        task_repo = TaskRepository(session)
        task_service = TaskService(task_repo, TranslationService(task_repo, TranslationClient()))
        
        task = await task_repo.get_task_by_id(task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")
            
        if not await task_service.delete_task(task_id):
            raise HTTPException(status_code=500, detail="Error deleting task")
