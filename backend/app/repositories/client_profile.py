"""
Client profile repository for client profile-related database operations.
"""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client_profile import ClientProfile
from app.repositories.base import BaseRepository
from app.schemas.client_profile import ClientProfileCreate, ClientProfileUpdate


class ClientProfileRepository(BaseRepository[ClientProfile, ClientProfileCreate, ClientProfileUpdate]):
    """
    Repository for ClientProfile model operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize client profile repository.
        
        Args:
            db: SQLAlchemy async session
        """
        super().__init__(ClientProfile, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> List[ClientProfile]:
        """
        Get all client profiles for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[ClientProfile]: List of client profiles
        """
        query = select(ClientProfile).where(ClientProfile.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_active_by_user_id(self, user_id: uuid.UUID) -> List[ClientProfile]:
        """
        Get active client profiles for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[ClientProfile]: List of active client profiles
        """
        query = select(ClientProfile).where(
            ClientProfile.user_id == user_id,
            ClientProfile.is_active == True
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_for_user(
        self, *, user_id: uuid.UUID, obj_in: ClientProfileCreate
    ) -> ClientProfile:
        """
        Create a client profile for a user.
        
        Args:
            user_id: User ID
            obj_in: Client profile creation data
            
        Returns:
            ClientProfile: Created client profile
        """
        db_obj = ClientProfile(
            user_id=user_id,
            name=obj_in.name,
            description=obj_in.description,
            industry=obj_in.industry,
            keywords=obj_in.keywords,
            is_active=obj_in.is_active,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def get_all_active(self) -> List[ClientProfile]:
        """
        Get all active client profiles across all users.
        This is particularly useful for batch processing articles for relevance.
        
        Returns:
            List[ClientProfile]: List of all active client profiles
        """
        query = select(ClientProfile).where(ClientProfile.is_active == True)
        result = await self.db.execute(query)
        return result.scalars().all()