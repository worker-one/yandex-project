# app/item/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload # Changed AsyncSession to Session

from app.database.core import get_db
from app.items import schemas as item_schemas
from app.items import service as item_service
from app.dependencies import get_current_active_user
from app.auth.models import User
from app.items.models import Item  # add this import

router = APIRouter(
    tags=["Items"],
    prefix="/items",
)

@router.get("/", response_model=item_schemas.ItemListResponse)
async def list_items(  # Changed async async def to async def
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name: str = Query(None),
    description: str = Query(None),
    owner_id: int = Query(None),
    sort_field: str = Query("id"),
    sort_direction: str = Query("asc"),
    db: Session = Depends(get_db)
):
    """
    List items with filtering, sorting, and pagination.
    """
    filters = item_schemas.ItemFilter(
        name=name,
        description=description,
        owner_id=owner_id
    )
    sort = item_schemas.ItemSort(
        field=sort_field,
        direction=sort_direction
    )
    items = item_service.item_service.list_items(  # Removed await
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort,
        options=[selectinload(Item.owner)]
    )
    return items

@router.post("/", response_model=item_schemas.ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: item_schemas.ItemCreate,
    db: Session = Depends(get_db), # Changed AsyncSession to Session
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new item.
    """
    item = item_service.item_service.create_item(db=db, item_in=item_in, owner_id=current_user.id) # Removed await
    db.refresh(item, attribute_names=["owner"]) # Removed await
    return item

@router.get("/{item_id}", response_model=item_schemas.ItemRead)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db) # Changed AsyncSession to Session
):
    """
    Get a specific item by its ID.
    """
    item = item_service.item_service.get_item_by_id(db=db, item_id=item_id, options=[selectinload(Item.owner)]) # Removed await
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=item_schemas.ItemRead)
async def update_item(
    item_id: int,
    item_in: item_schemas.ItemUpdate,
    db: Session = Depends(get_db), # Changed AsyncSession to Session
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an item.
    """
    item = item_service.item_service.get_item_by_id(db=db, item_id=item_id, options=[selectinload(Item.owner)]) # Removed await
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    updated_item = item_service.item_service.update_item(db=db, item=item, item_in=item_in) # Removed await
    db.refresh(updated_item, attribute_names=["owner"]) # Removed await
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db), # Changed AsyncSession to Session
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an item.
    """
    item = item_service.item_service.get_item_by_id(db=db, item_id=item_id, options=[selectinload(Item.owner)]) # Removed await
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    item_service.item_service.delete_item(db=db, item=item) # Removed await
    return None
