# app/main.py
from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.config import settings
from app.auth.router import router as auth_router
from app.devices.router import router as devices_router
from app.mqtt.service import initialize_mqtt_service
from app.devices.mqtt_service import device_mqtt_service

if settings.ENVIRONMENT == "local":
    LOG_LEVEL = "debug"  # Set log level to debug for local development
else:
    LOG_LEVEL = "info"

# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
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


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    if settings.MQTT_ENABLED:
        try:
            # Initialize MQTT service
            await initialize_mqtt_service(
                broker_host=settings.MQTT_BROKER_HOST,
                broker_port=settings.MQTT_BROKER_PORT,
                username=settings.MQTT_USERNAME,
                password=settings.MQTT_PASSWORD
            )
            
            # Register device status callback
            await device_mqtt_service.register_device_status_callback()
            
            print("MQTT service initialized successfully")
        except Exception as e:
            print(f"Failed to initialize MQTT service: {e}")
            print("Application will continue without MQTT support")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if settings.MQTT_ENABLED:
        try:
            from app.mqtt.service import get_mqtt_service
            mqtt_service = await get_mqtt_service()
            await mqtt_service.disconnect()
            print("MQTT service disconnected")
        except Exception as e:
            print(f"Error disconnecting MQTT service: {e}")


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
    from app.database.core import init_db
    # Initialize the database connection
    init_db()
    # Run the app with Uvicorn if this file is executed directly
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level=LOG_LEVEL)
