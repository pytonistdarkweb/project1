from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.domain.schemas.user import UserCreate, UserResponse
from app.domain.schemas.token import Token
from app.application.auth_services import UserAuthService, TokenService
from app.Infrastructure.repository.user_repository import UserRepository
from app.Infrastructure.database import AsyncSessionLocal

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        auth_service = UserAuthService(user_repo)
        return await auth_service.create_user(user_data)

@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        auth_service = UserAuthService(user_repo)
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token, refresh_token = TokenService.create_tokens({"sub": user.username})
        return Token(access_token=access_token, refresh_token=refresh_token)
