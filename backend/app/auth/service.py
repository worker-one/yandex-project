from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional

from .models import User
from app.auth import schemas, security

class AuthService:

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        result = db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    def get_user_by_name(self, db: Session, name: str) -> Optional[User]:
        result = db.execute(select(User).filter(User.name == name))
        return result.scalar_one_or_none()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        result = db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    def create_user(self, db: Session, user_in: schemas.UserCreate) -> User:
        # Check if email exists
        existing_user = self.get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )
        # Check if name exists
        existing_name = self.get_user_by_name(db, name=user_in.name)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nickname already taken.",
            )

        hashed_password = security.get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            name=user_in.name,
            avatar_url=user_in.avatar_url,
            password_hash=hashed_password,
            is_superuser=False, # Default to non-admin
            # email_verified_at=None # Requires email verification flow
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(db, email=email)
        if not user:
            return None
        if not security.verify_password(password, user.password_hash):
            return None
        # Add checks for active status or verified email if needed
        # if not user.is_active: return None
        return user

    def update_user_profile(self, db: Session, db_user: User, user_in: schemas.UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != db_user.name:
             # Check if new name exists
            existing_name = self.get_user_by_name(db, name=update_data["name"])
            if existing_name and existing_name.id != db_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nickname already taken.",
                )
            db_user.name = update_data["name"]

        if "avatar_url" in update_data:
             db_user.avatar_url = update_data["avatar_url"]

        db.commit()
        db.refresh(db_user)
        return db_user

    def update_user_password(self, db: Session, db_user: User, password_in: schemas.UserPasswordUpdate) -> User:
        if not security.verify_password(password_in.current_password, db_user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")

        hashed_password = security.get_password_hash(password_in.new_password)
        db_user.password_hash = hashed_password
        db.commit()
        # No need to refresh db_user here unless password_hash is needed immediately
        return db_user


auth_service = AuthService()