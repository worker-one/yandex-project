from sqlalchemy import (
    Column, Integer, String, ForeignKey
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
    serial_number = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # relationship fields
    owner = relationship(
        "User", 
        back_populates="items",
        foreign_keys=[user_id]
    )
