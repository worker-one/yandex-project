# app/models/user.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean
)
from sqlalchemy.orm import relationship

from app.models import Base, TimeStampMixin
from app.items.models import Item  # or use a string if circular import

class User(Base, TimeStampMixin):
    """
    SQLAlchemy model for users.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True, index=True) # Index email for faster lookups
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False, unique=True, index=True) # Index name too
    avatar_url = Column(String(512), nullable=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True) # Optional: If user blocking is needed

    # --- Relationships ---
    # Items created by this user
    items = relationship("Item", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"