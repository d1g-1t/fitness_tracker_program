from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from src.models.models import User
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash, verify_password
from typing import Optional
from src.core.logging import get_logger


logger = get_logger(__name__)


class UserService:
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        logger.info(f"Создание нового пользователя: {user_data.username}")
        
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            age=user_data.age,
            weight=user_data.weight,
            height=user_data.height,
            gender=user_data.gender,
        )
        
        db.add(user)
        await db.flush()
        await db.refresh(user)
        
        logger.info(f"Пользователь создан успешно: ID {user.id}")
        return user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        logger.info(f"Попытка аутентификации пользователя: {username}")
        
        user = await UserService.get_user_by_username(db, username)
        
        if not user:
            logger.warning(f"Пользователь не найден: {username}")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Неверный пароль для пользователя: {username}")
            return None
        
        logger.info(f"Пользователь успешно аутентифицирован: {username}")
        return user
    
    @staticmethod
    async def update_user(
        db: AsyncSession, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        logger.info(f"Обновление данных пользователя: ID {user_id}")
        
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"Пользователь не найден для обновления: ID {user_id}")
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.flush()
        await db.refresh(user)
        
        logger.info(f"Пользователь обновлен успешно: ID {user_id}")
        return user
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        logger.info(f"Удаление пользователя: ID {user_id}")
        
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"Пользователь не найден для удаления: ID {user_id}")
            return False
        
        await db.delete(user)
        logger.info(f"Пользователь удален успешно: ID {user_id}")
        return True
