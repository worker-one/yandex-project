# app/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query, Form
from sqlalchemy.orm import Session # Changed from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List # Add List
from fastapi.responses import RedirectResponse
import uuid
from threading import Lock

from ..database.core import get_db

from . import schemas
from .service import auth_service # Ensure auth_service is imported correctly
from . import security
from ..dependencies import get_current_active_user
from .models import User
from .. import schemas as common_schemas
from ..devices import schemas as device_schemas
from ..devices.service import device_service as global_device_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication & Profile"]
)

# --- In-memory code store for demo OAuth flow ---
oauth_code_store = {}
oauth_code_store_lock = Lock()

@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user( # Changed async async def to async def
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db) # Changed AsyncSession to Session
):
    """
    Register a new user.
    """
    db_user = auth_service.create_user(db=db, user_in=user_in) # Removed await (already done in input)
    return db_user

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token( # Changed async async def to async def
    db: Session = Depends(get_db), # Changed AsyncSession to Session
    form_data: schemas.LoginRequest = Body(...) # Use Body for JSON payload
):
    """
    Authenticate user and return access and refresh tokens.
    """
    email = form_data.email if form_data.email else form_data.username
    user = auth_service.authenticate_user( # Removed await (already done in input)
        db, email=form_data.email, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(subject=user.id)
    refresh_token = security.create_refresh_token(subject=user.id)

    return schemas.Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token( # Changed async async def to async def
    refresh_request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db) # Changed AsyncSession to Session
):
    """
    Get a new access token using a refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_token(refresh_request.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    user = auth_service.get_user_by_id(db=db, user_id=user_id) # Removed await (already done in input)
    if user is None:
        raise credentials_exception # User might have been deleted

    # Generate new tokens
    new_access_token = security.create_access_token(subject=user.id)
    # Optionally, generate a new refresh token as well for rotation
    new_refresh_token = security.create_refresh_token(subject=user.id)

    return schemas.Token(access_token=new_access_token, refresh_token=new_refresh_token)


# --- Profile Endpoints ---

CurrentUser = Annotated[User, Depends(get_current_active_user)]

@router.get("/profile", response_model=schemas.UserRead)
async def read_users_me(current_user: CurrentUser): # Changed async async def to async def
    """
    Get current logged-in user's profile.
    """
    return current_user

@router.patch("/profile", response_model=schemas.UserRead)
async def update_users_me( # Changed async async def to async def
    user_in: schemas.UserUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db), # Changed AsyncSession to Session
):
    """
    Update current logged-in user's profile (name, avatar).
    """
    updated_user = auth_service.update_user_profile(db=db, db_user=current_user, user_in=user_in) # Removed await (already done in input)
    return updated_user

@router.put("/profile/password", response_model=common_schemas.Message)
async def update_users_password( # Changed async async def to async def
    password_in: schemas.UserPasswordUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db), # Changed AsyncSession to Session
):
    """
    Update current logged-in user's password.
    """
    auth_service.update_user_password(db=db, db_user=current_user, password_in=password_in)
    return common_schemas.Message(message="Password updated successfully")

# --- Yandex OAuth Callback Endpoint ---
@router.post("/yandex/callback", response_model=schemas.YandexCallbackResponseData)
async def handle_yandex_callback(
    data: dict = Body(...),  # Accept JSON body
    db: Session = Depends(get_db)
):
    """
    Handle Yandex OAuth callback.
    Exchanges Yandex code for Yandex token, fetches Yandex user info,
    finds or creates a local user, and returns app-specific tokens and user profile.
    The frontend should use these tokens to log the user in.
    """
    code = data.get("code")
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Yandex OAuth code."
        )
    try:
        user = auth_service.process_yandex_oauth_callback(db=db, code=code)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in Yandex callback: {e}") # Basic logging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during Yandex authentication."
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate with Yandex."
        )

    app_access_token = security.create_access_token(subject=user.id)
    app_refresh_token = security.create_refresh_token(subject=user.id)
    user_profile = schemas.UserRead.from_orm(user)
    print(f"Yandex OAuth successful for user: {user.email}")

    return schemas.YandexCallbackResponseData(
        access_token=app_access_token,
        refresh_token=app_refresh_token,
        user_profile=user_profile
    )

# --- Yandex IoT Endpoints ---
@router.post("/profile/yandex-iot/sync-devices", response_model=List[device_schemas.DeviceRead], status_code=status.HTTP_200_OK)
def sync_yandex_iot_devices_endpoint(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Fetch devices from user's Yandex IoT account and sync them as devices.
    """
    if not current_user.yandex_oauth_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yandex account not linked or Yandex OAuth token not available. Please authenticate with Yandex first."
        )
    
    try:
        synced_devices = auth_service.sync_user_yandex_iot_devices(
            db=db, 
            user=current_user, 
            device_service_instance=global_device_service
        )
        return synced_devices
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error during Yandex IoT device sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during Yandex IoT device synchronization."
        )

@router.get("/authorize")
def oauth_authorize_endpoint(
    response_type: str = Query(..., description="OAuth response type, e.g., 'code'"),
    client_id: str = Query(..., description="OAuth client ID"),
    redirect_uri: str = Query(..., description="OAuth redirect URI"),
    scope: str = Query("", description="OAuth scopes (space-separated)"),
    state: str = Query(None, description="Opaque value for CSRF protection"),
):
    """
    OAuth 2.0 Authorization Endpoint (RFC 6749 section 3.1).
    This is where the user would authenticate and authorize the client.
    """
    if response_type != "code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported response_type"
        )
    # TODO: Validate client_id, redirect_uri, and implement user consent/authentication

    # Simulate successful authorization and generate a unique code
    code = str(uuid.uuid4())
    # For demo: associate code with user_id=1
    with oauth_code_store_lock:
        oauth_code_store[code] = {"user_id": 1}

    from urllib.parse import urlencode
    params = {"code": code}
    if state:
        params["state"] = state
    redirect_url = f"{redirect_uri}?{urlencode(params)}"
    return RedirectResponse(url=redirect_url)

@router.post("/token")
async def oauth_token_endpoint(
    grant_type: str = Form(..., description="OAuth grant type, e.g., 'authorization_code'"),
    code: str = Form(..., description="The authorization code received from the /authorize endpoint"),
    client_secret: str = Form(..., description="The client secret (OAuth token of the skill)"),
    redirect_uri: str = Form(None, description="The redirect URI used in the authorization request"),
    client_id: str = Form(None, description="The client ID"),
    db: Session = Depends(get_db),
):
    """
    OAuth 2.0 Token Endpoint (RFC 6749 section 3.2).
    Exchanges authorization code for access token.
    """
    print(f"Token endpoint called with:")
    print(f"  grant_type: {grant_type}")
    print(f"  code: {code}")
    print(f"  client_secret: {client_secret[:10]}..." if client_secret else "None")
    print(f"  redirect_uri: {redirect_uri}")
    print(f"  client_id: {client_id}")
    
    if grant_type != "authorization_code":
        print(f"ERROR: Unsupported grant_type: {grant_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant_type"
        )
    
    # TODO: Validate client_id and client_secret if necessary
    # For now, we trust the code as it's single-use and short-lived.
    
    # Validate code
    print(f"Checking code in store. Current codes: {list(oauth_code_store.keys())}")
    with oauth_code_store_lock:
        code_data = oauth_code_store.pop(code, None)
    
    if not code_data:
        print(f"ERROR: Code '{code}' not found in store or already used")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired authorization code"
        )
    
    print(f"Code validated, associated with user_id: {code_data['user_id']}")
    user_id = code_data["user_id"]
    user = auth_service.get_user_by_id(db=db, user_id=user_id)
    if not user:
        print(f"ERROR: User with id {user_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    print(f"User found: {user.email}, generating tokens...")
    access_token = security.create_access_token(subject=user.id)
    refresh_token = security.create_refresh_token(subject=user.id)

    print("Tokens generated successfully, returning response")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }
