"""
API routes for client profile management.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.client_profile import ClientProfileRepository
from app.schemas.client_profile import ClientProfile, ClientProfileCreate, ClientProfileUpdate

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("", response_model=List[ClientProfile])
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all client profiles for the current user.
    
    Args:
        skip: Number of profiles to skip
        limit: Maximum number of profiles to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[ClientProfile]: List of client profiles
    """
    client_repo = ClientProfileRepository(db)
    clients = await client_repo.get_by_user_id(current_user.id)
    
    # Apply pagination
    paginated_clients = clients[skip:skip + limit]
    
    return paginated_clients


@router.post("", response_model=ClientProfile, status_code=status.HTTP_201_CREATED)
async def create_client_profile(
    client_in: ClientProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new client profile.
    
    Args:
        client_in: Client profile creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClientProfile: Created client profile
    """
    client_repo = ClientProfileRepository(db)
    client = await client_repo.create_for_user(user_id=current_user.id, obj_in=client_in)
    return client


@router.get("/{client_id}", response_model=ClientProfile)
async def get_client_profile(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a client profile by ID.
    
    Args:
        client_id: Client profile ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClientProfile: Client profile
    """
    client_repo = ClientProfileRepository(db)
    client = await client_repo.get(id=client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    # Check if the client profile belongs to the current user
    if client.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this client profile"
        )
    
    return client


@router.put("/{client_id}", response_model=ClientProfile)
async def update_client_profile(
    client_id: uuid.UUID,
    client_in: ClientProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a client profile.
    
    Args:
        client_id: Client profile ID
        client_in: Client profile update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ClientProfile: Updated client profile
    """
    client_repo = ClientProfileRepository(db)
    client = await client_repo.get(id=client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    # Check if the client profile belongs to the current user
    if client.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this client profile"
        )
    
    updated_client = await client_repo.update(db_obj=client, obj_in=client_in)
    return updated_client


@router.delete("/{client_id}", status_code=status.HTTP_200_OK)
async def delete_client_profile(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a client profile.
    
    Args:
        client_id: Client profile ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Success message
    """
    client_repo = ClientProfileRepository(db)
    client = await client_repo.get(id=client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    # Check if the client profile belongs to the current user
    if client.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this client profile"
        )
    
    await client_repo.remove(id=client_id)
    
    return {"success": True}