from datetime import datetime, timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from app.domain.schemas.token import Token, TokenData
from app.core.security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from passlib.context import CryptContext
from sqlalchemy import select 
from app.Infrastructure.database import AsyncSessionLocal
from jose import jwt
from fastapi import HTTPException, status
from app.domain.models.user import User
from app.domain.schemas.user import UserCreate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class SecurityService:
    """Сервис для работы с безопасностью и шифрованием"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
        
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

class TokenService:
    """Сервис для работы с токенами"""
    
    @staticmethod
    def create_tokens(data: dict) -> tuple[str, str]:
        """Создает пару access и refresh токенов"""
        access_token = TokenService._create_token(
            data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = TokenService._create_token(
            data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        return access_token, refresh_token
    
    @staticmethod
    def _create_token(data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> TokenData:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            return TokenData(username=username)
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

class UserAuthService:
    """Сервис аутентификации пользователей"""
    
    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        user = await UserAuthService.get_user(username)
        if not user or not SecurityService.verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    async def get_user(username: str) -> Optional[User]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()
            
    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        async with AsyncSessionLocal() as db:
            # Проверка существования пользователя
            existing_user = await db.execute(
                select(User).where(
                    (User.username == user_data.username) | 
                    (User.email == user_data.email)
                )
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already registered"
                )
            
            # Создание нового пользователя
            hashed_password = SecurityService.get_password_hash(user_data.password)
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=hashed_password
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user



