from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.endpoints.auth import auth_router
from app.api.endpoints.tasks import tasks_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при запуске
    from app.Infrastructure.database import init_db
    await init_db()
    yield
    # Очистка при выключении
    from app.Infrastructure.database import close_db
    await close_db()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks"])

# Корневой эндпоинт
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Task Management API",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }        