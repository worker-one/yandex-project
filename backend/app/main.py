# app/main.py
from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.auth.router import router as auth_router
from app.devices.router import router as devices_router
from app.mqtt import mqtt_client

logger = logging.getLogger(__name__)

if settings.ENVIRONMENT == "local":
    LOG_LEVEL = "debug"  # Set log level to debug for local development
else:
    LOG_LEVEL = "info"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    mqtt_client.connect()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    mqtt_client.disconnect()

# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    # swagger
    docs_url=f"{settings.API_V1_STR}/docs",  # Customize Swagger UI path
    openapi_url=f"{settings.API_V1_STR}/openapi.json" # Customize OpenAPI path
    
)

# --- Middleware ---
# Set up CORS (Cross-Origin Resource Sharing)
origins = [
    "*"
    # Add other allowed origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- Routers ---
# Include modular routers
api_router_v1 = APIRouter() # Create a router for versioning
api_router_v1.include_router(auth_router)
api_router_v1.include_router(devices_router)

app.include_router(api_router_v1, prefix=settings.API_V1_STR)


from app.mqtt import mqtt_client

# Health check endpoint via HEAD
@app.head(f"{settings.API_V1_STR}/", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    Returns 200 OK response.
    """
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    from app.database.core import init_db, drop_db
    # Initialize the database connection
    drop_db(cascade=True)  # Use CASCADE to drop dependent objects
    init_db()
    # Run the app with Uvicorn if this file is executed directly
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level=LOG_LEVEL)
    init_db()
    # Run the app with Uvicorn if this file is executed directly
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level=LOG_LEVEL)
