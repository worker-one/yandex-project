from sqlalchemy import (
    Boolean, Column, Integer, String, Text, ForeignKey, DateTime  # Added DateTime
)
from sqlalchemy.orm import relationship

# Import Base from the central location
from ..models import Base, TimeStampMixin

class Item(Base, TimeStampMixin):
    """
    Generic base model for rankable items (Exchanges, Books, etc.).
    Uses joined table inheritance.
    """
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    position = Column(Integer, default=0)  # 0-100
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime)

    # relationship fields
    owner = relationship(
        "User", 
        back_populates="items",
        foreign_keys=[user_id]  # Corrected from owner_id to user_id
    )
