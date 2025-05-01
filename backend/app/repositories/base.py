"""
Base repository for database operations.
"""
import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository with CRUD operations for all models.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository with model and database session.
        
        Args:
            model: SQLAlchemy model class
            db: SQLAlchemy async session
        """
        self.model = model
        self.db = db

    async def get(self, id: uuid.UUID) -> Optional[ModelType]:
        """
        Get a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Optional[ModelType]: Record if found, None otherwise
        """
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[ModelType]: List of records
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            obj_in: Data for record creation

        Returns:
            ModelType: Created record
        """
        # Create a dictionary directly from the Pydantic model's attributes
        # Use exclude_unset=True if you only want fields that were explicitly set
        # Use exclude_none=True if you want to skip fields with None values
        # Choose the options that make sense for your create logic.
        # For a standard create, exclude_unset might not be needed if all fields are required
        # or have defaults. .dict() is often sufficient.
        obj_in_data = obj_in.dict()

        # Or, if you need more control or specific exclusions:
        # obj_in_data = obj_in.dict(exclude={"field_to_exclude"})

        # DO NOT use jsonable_encoder here for passing data to SQLAlchemy models.

        # Instantiate the SQLAlchemy model using the dictionary
        # that retains the correct Python types (like datetime objects).
        db_obj = self.model(**obj_in_data)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.

        Args:
            db_obj: Record to update
            obj_in: Data for record update

        Returns:
            ModelType: Updated record
        """
        # Get update data dictionary, excluding unset fields
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Use exclude_unset=True to only apply fields present in the update schema
            update_data = obj_in.dict(exclude_unset=True)

        # Iterate through the update data and set attributes on the SQLAlchemy object
        for field, value in update_data.items():
             # Check if the field exists on the model to avoid errors
             if hasattr(db_obj, field):
                 setattr(db_obj, field, value) # Directly set the attribute

        self.db.add(db_obj) # Add the updated object to the session
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def remove(self, *, id: uuid.UUID) -> Optional[ModelType]:
        """
        Remove a record.
        
        Args:
            id: Record ID
            
        Returns:
            Optional[ModelType]: Removed record if found, None otherwise
        """
        obj = await self.get(id=id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj