"""
User repository for user-related database operations.
"""
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    Repository for User model operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize user repository.
        
        Args:
            db: SQLAlchemy async session
        """
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: User email
            
        Returns:
            Optional[User]: User if found, None otherwise
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            obj_in: User creation data
            
        Returns:
            User: Created user
        """
        db_obj = User(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=True,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update_password(self, *, user_id: uuid.UUID, new_password: str) -> Optional[User]:
        """
        Update user password.
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            Optional[User]: Updated user if found, None otherwise
        """
        user = await self.get(id=user_id)
        if not user:
            return None
            
        user.password_hash = get_password_hash(new_password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user