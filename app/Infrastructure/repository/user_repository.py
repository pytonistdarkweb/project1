from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from typing import Optional, List
from app.domain.models.user import User
from datetime import datetime

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, username: str, email: str, password_hash: str) -> User:
        user = User(
            username=username, 
            email=email, 
            password_hash=password_hash
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_active_users(self) -> List[User]:
        result = await self.session.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()

    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            setattr(user, key, value)
        
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def deactivate_user(self, user_id: int) -> bool:
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount > 0

    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return True
        return False

    async def check_user_exists(self, username: str = None, email: str = None) -> bool:
        conditions = []
        if username:
            conditions.append(User.username == username)
        if email:
            conditions.append(User.email == email)
        
        if not conditions:
            return False

        result = await self.session.execute(
            select(User).where(and_(*conditions))
        )
        return result.first() is not None

    async def update_password(self, user_id: int, new_password_hash: str) -> bool:
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                password_hash=new_password_hash,
                updated_at=datetime.utcnow()
            )
        )
        await self.session.commit()
        return result.rowcount > 0