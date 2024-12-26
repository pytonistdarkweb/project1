from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.application.auth_services import TokenService, UserAuthService
from app.Infrastructure.database import AsyncSessionLocal
from app.Infrastructure.repository.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = TokenService.verify_token(token)
        if token_data.username is None:
            raise credentials_exception
    except:
        raise credentials_exception
        
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        auth_service = UserAuthService(user_repo)
        user = await auth_service.get_user(token_data.username)
        if user is None:
            raise credentials_exception
        return user 