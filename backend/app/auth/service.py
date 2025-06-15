import httpx # For making HTTP requests to Yandex
import secrets # For generating random passwords if needed
from typing import Optional, List, Dict, Any # Add List, Dict, Any
from sqlalchemy import select # Add select import
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta # Add datetime, timedelta

from . import models, schemas, security # Assuming security.py has get_password_hash
from .models import User # Add User model import
from ..core.config import settings # Import settings
from ..items import service as item_service_module # For type hinting and access to ItemService
from ..items import schemas as item_schemas # For creating item schemas
from ..items import models as item_models # For type hinting

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

    def get_user_by_yandex_id(self, db: Session, yandex_id: str) -> Optional[models.User]:
        # This assumes your User model has a 'yandex_id' field
        # return db.query(models.User).filter(models.User.yandex_id == yandex_id).first()
        # If not, you might need to adjust this logic or rely solely on email.
        # For now, returning None to avoid error if field doesn't exist.
        if hasattr(models.User, 'yandex_id'):
            # Corrected to use select
            result = db.execute(select(models.User).filter(models.User.yandex_id == yandex_id))
            return result.scalar_one_or_none()
        return None


    YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
    YANDEX_USERINFO_URL = "https://login.yandex.ru/info?format=json"
    # YANDEX_IOT_API_BASE_URL will be accessed via settings.YANDEX_IOT_API_BASE_URL

    def _refresh_yandex_oauth_token(self, db: Session, user: models.User) -> str:
        """Refreshes the Yandex OAuth access token using the refresh token."""
        if not user.yandex_oauth_refresh_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Yandex refresh token available for user.")

        token_payload = {
            "grant_type": "refresh_token",
            "refresh_token": user.yandex_oauth_refresh_token,
            "client_id": settings.YANDEX_CLIENT_ID,
            "client_secret": settings.YANDEX_CLIENT_SECRET,
        }
        try:
            with httpx.Client() as client:
                token_response = client.post(self.YANDEX_TOKEN_URL, data=token_payload)
                token_response.raise_for_status()
                new_yandex_tokens = token_response.json()
        except httpx.HTTPStatusError as e:
            # If refresh fails (e.g. invalid refresh token), clear tokens to force re-auth
            user.yandex_oauth_access_token = None
            user.yandex_oauth_refresh_token = None
            user.yandex_oauth_token_expires_at = None
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to refresh Yandex token, re-authentication required: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during Yandex token refresh: {str(e)}"
            )

        user.yandex_oauth_access_token = new_yandex_tokens["access_token"]
        # Yandex might issue a new refresh token, update if provided
        if "refresh_token" in new_yandex_tokens:
            user.yandex_oauth_refresh_token = new_yandex_tokens["refresh_token"]
        user.yandex_oauth_token_expires_at = datetime.utcnow() + timedelta(seconds=new_yandex_tokens["expires_in"])
        
        db.commit()
        db.refresh(user)
        return user.yandex_oauth_access_token

    def _fetch_yandex_iot_user_info(self, db: Session, user: models.User) -> Dict[str, Any]:
        """Fetches user info (including devices) from Yandex IoT API."""
        if not user.yandex_oauth_access_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Yandex access token not available.")

        access_token = user.yandex_oauth_access_token
        if user.yandex_oauth_token_expires_at and user.yandex_oauth_token_expires_at <= datetime.utcnow():
            print("Yandex OAuth token expired, attempting refresh.")
            access_token = self._refresh_yandex_oauth_token(db, user)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{settings.YANDEX_IOT_API_BASE_URL}/v1.0/user/info"
        
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers)
                if response.status_code == 401: # Token might have been revoked or expired just now
                    print("Yandex IoT API returned 401, attempting token refresh and retry.")
                    access_token = self._refresh_yandex_oauth_token(db, user)
                    headers = {"Authorization": f"Bearer {access_token}"}
                    response = client.get(url, headers=headers) # Retry with new token
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to fetch Yandex IoT user info: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during Yandex IoT user info fetch: {str(e)}"
            )

    def sync_user_yandex_iot_devices(
        self, db: Session, user: models.User, item_service_instance: item_service_module.ItemService
    ) -> List[item_schemas.ItemRead]:
        """Fetches Yandex IoT devices for the user and syncs them as items."""
        iot_user_info = self._fetch_yandex_iot_user_info(db, user)
        
        yandex_devices = iot_user_info.get("devices", [])
        synced_items_pydantic = []

        for device in yandex_devices:
            external_id = device.get("id")
            if not external_id:
                continue # Skip devices without an ID

            name = device.get("name", "Unnamed Yandex Device")
            description_parts = []
            if device.get("room"):
                description_parts.append(f"Room: {device.get('room')}")
            if device.get("type"):
                description_parts.append(f"Type: {device.get('type')}")
            description = ", ".join(description_parts) or "Yandex IoT Device"

            item_create_schema = item_schemas.ItemCreate(
                name=name,
                description=description,
                user_id=user.id, # Explicitly set user_id
                external_id=external_id,
                external_source="yandex_iot"
            )
            
            # create_item will check for existence and return existing or new
            # owner_id is used by create_item to set user_id, but we've set it in schema
            item_model = item_service_instance.create_item(
                db=db, item_in=item_create_schema, owner_id=user.id 
            )
            db.refresh(item_model, attribute_names=["owner"]) # Ensure owner is loaded for ItemRead
            synced_items_pydantic.append(
                item_schemas.ItemRead.model_validate(item_model, from_attributes=True)
            )
        
        return synced_items_pydantic

    def process_yandex_oauth_callback(self, db: Session, code: str) -> models.User:
        # 1. Exchange authorization code for Yandex access token
        token_payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.YANDEX_CLIENT_ID,
            "client_secret": settings.YANDEX_CLIENT_SECRET,
            # "redirect_uri": settings.YANDEX_REDIRECT_URI # Yandex might not require it here if already matched
        }
        try:
            # Corrected to use self.YANDEX_TOKEN_URL
            with httpx.Client() as client:
                token_response = client.post(self.YANDEX_TOKEN_URL, data=token_payload)
                token_response.raise_for_status() # Raise an exception for HTTP errors
                yandex_tokens = token_response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange Yandex code: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during Yandex token exchange: {str(e)}"
            )

        yandex_access_token = yandex_tokens.get("access_token")
        yandex_refresh_token = yandex_tokens.get("refresh_token")
        expires_in = yandex_tokens.get("expires_in")

        if not yandex_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yandex did not return an access token."
            )

        # 2. Fetch user information from Yandex
        headers = {"Authorization": f"OAuth {yandex_access_token}"}
        try:
            # Corrected to use self.YANDEX_USERINFO_URL
            with httpx.Client() as client:
                userinfo_response = client.get(self.YANDEX_USERINFO_URL, headers=headers)
                userinfo_response.raise_for_status()
                yandex_user_info = userinfo_response.json()
                print(yandex_user_info)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch Yandex user info: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during Yandex user info fetch: {str(e)}"
            )

        yandex_id = str(yandex_user_info.get("id"))
        email = yandex_user_info.get("default_email")
        name = yandex_user_info.get("display_name") or yandex_user_info.get("real_name") or yandex_user_info.get("login")
        # avatar_id = yandex_user_info.get("default_avatar_id")
        # avatar_url = f"https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200" if avatar_id else None


        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Yandex. Ensure your Yandex app requests email permission."
            )

        # 3. Find or create user in local database
        user = self.get_user_by_yandex_id(db, yandex_id=yandex_id) # Corrected: self.
        if user:
            print(f"Found existing user by Yandex ID: {user.email}")
            # Update tokens and other info if necessary
            user.yandex_oauth_access_token = yandex_access_token
            if yandex_refresh_token:
                user.yandex_oauth_refresh_token = yandex_refresh_token
            if expires_in:
                user.yandex_oauth_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            if user.name != name: user.name = name # Update name if different
            # if hasattr(user, 'avatar_url') and avatar_url and user.avatar_url != avatar_url: user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)
            return user

        # User not found by yandex_id, try by email
        user = self.get_user_by_email(db, email=email) # Corrected: self.
        if user:
            print(f"Found existing user by email: {user.email}, linking Yandex ID and tokens.")
            # User with this email exists. Link Yandex ID and store tokens.
            if hasattr(user, 'yandex_id') and not user.yandex_id:
                user.yandex_id = yandex_id
            user.yandex_oauth_access_token = yandex_access_token
            if yandex_refresh_token:
                user.yandex_oauth_refresh_token = yandex_refresh_token
            if expires_in:
                user.yandex_oauth_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            # if name and user.name != name: user.name = name
            # if hasattr(user, 'avatar_url') and avatar_url: user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)
            return user
        # Create new user if not found by yandex_id or email
        # For OAuth users, password is not set directly by them.
        # Generate a secure random password or ensure your UserCreate schema/model handles None password.
        # If UserCreate requires a password:
        random_password = secrets.token_urlsafe(16)
        user_in_create = schemas.UserCreate(email=email, name=name, password=random_password)
        
        # Assuming 'create_user' hashes the password and saves the user.
        new_user = self.create_user(db, user_in=user_in_create) # Corrected: self.

        # Link Yandex ID and store tokens for the new user
        if hasattr(new_user, 'yandex_id'):
            new_user.yandex_id = yandex_id
        new_user.yandex_oauth_access_token = yandex_access_token
        if yandex_refresh_token:
            new_user.yandex_oauth_refresh_token = yandex_refresh_token
        if expires_in:
            new_user.yandex_oauth_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        # if hasattr(new_user, 'avatar_url') and avatar_url:
        #     new_user.avatar_url = avatar_url
        
        # Mark user as active, etc., if needed
        # new_user.is_active = True 
        
        db.commit()
        db.refresh(new_user)
        return new_user


auth_service = AuthService()