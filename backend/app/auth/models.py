# app/models/user.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean
)
from sqlalchemy.orm import relationship

from app.models import Base, TimeStampMixin
from app.devices.models import Item  # or use a string if circular import

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
    yandex_oauth_access_token = Column(String, nullable=True)
    yandex_oauth_refresh_token = Column(String, nullable=True)
    yandex_oauth_token_expires_at = Column(DateTime, nullable=True)
    yandex_id = Column(String, nullable=True, unique=True, index=True) # Add Yandex ID
    is_superuser = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True) # Optional: If user blocking is needed

    # --- Relationships ---
    # Devices created by this user
    devices = relationship("Item", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"