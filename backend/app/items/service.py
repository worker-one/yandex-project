# app/item/service.py
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from typing import Optional, List
import logging

from app.items import models as item_models
from app.items import schemas as item_schemas

# Get logger
logger = logging.getLogger(__name__)

class ItemService:
    def get_item_by_id(self, db: Session, item_id: int, options: List = None) -> Optional[item_models.Item]:
        """Retrieve a single item by its ID."""
        logger.info(f"Retrieving item with id {item_id}.")
        query = db.query(item_models.Item)
        if options:
            query = query.options(*options)
        item = query.filter(item_models.Item.id == item_id).first()
        logger.info(f"Item with id {item_id} {'found' if item else 'not found'}.")
        return item

    def list_items(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: item_schemas.ItemFilter = None,
        sort: item_schemas.ItemSort = None,
        options: List = None
    ):
        """
        Retrieve a list of items with optional filtering, sorting, and pagination.
        """
        query = select(item_models.Item)

        # Filtering
        if filters:
            if filters.name is not None:
                query = query.where(item_models.Item.name.ilike(f"%{filters.name}%"))
            if filters.description is not None:
                query = query.where(item_models.Item.description.ilike(f"%{filters.description}%"))
            if filters.owner_id is not None:
                query = query.where(item_models.Item.owner_id == filters.owner_id)

        # Sorting
        if sort:
            sort_field = getattr(item_models.Item, sort.field, None)
            if sort_field is not None:
                if sort.direction == "desc":
                    query = query.order_by(desc(sort_field))
                else:
                    query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(asc(item_models.Item.id))

        query = query.options(*(options or []))

        # Count total
        total_query = select(item_models.Item.id)
        if filters:
            if filters.name is not None:
                total_query = total_query.where(item_models.Item.name.ilike(f"%{filters.name}%"))
            if filters.description is not None:
                total_query = total_query.where(item_models.Item.description.ilike(f"%{filters.description}%"))
            if filters.owner_id is not None:
                total_query = total_query.where(item_models.Item.owner_id == filters.owner_id)
        total_result = db.execute(total_query)
        total = len(total_result.scalars().all())

        # Pagination
        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        items = result.scalars().all()

        # Convert SQLAlchemy models to Pydantic models
        items_read = [item_schemas.ItemRead.model_validate(item, from_attributes=True) for item in items]

        return item_schemas.ItemListResponse(
            items=items_read,
            total=total
        )

    def create_item(self, db: Session, item_in: item_schemas.ItemCreate, owner_id: Optional[int] = None) -> item_models.Item:
        """Create a new item."""
        item = item_models.Item(**item_in.dict(), owner_id=owner_id)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_item(self, db: Session, item: item_models.Item, item_in: item_schemas.ItemUpdate) -> item_models.Item:
        """Update an existing item."""
        for field, value in item_in.dict(exclude_unset=True).items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    def delete_item(self, db: Session, item: item_models.Item) -> None:
        """Delete an item."""
        db.delete(item)
        db.commit()

item_service = ItemService()