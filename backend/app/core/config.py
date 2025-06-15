import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Yandex OAuth Configuration
    YANDEX_CLIENT_ID: str = os.getenv("YANDEX_CLIENT_ID", "YOUR_YANDEX_CLIENT_ID")
    YANDEX_CLIENT_SECRET: str = os.getenv("YANDEX_CLIENT_SECRET", "YOUR_YANDEX_CLIENT_SECRET")
    # This redirect URI must match the one configured in your Yandex App settings
    # and the one used by your frontend to initiate OAuth flow.
    YANDEX_REDIRECT_URI: str = os.getenv("YANDEX_REDIRECT_URI", "http://localhost:3000/auth/yandex/callback")
    YANDEX_IOT_API_BASE_URL: str = os.getenv("YANDEX_IOT_API_BASE_URL", "https://api.iot.yandex.net")
    # JWT settings (already used by your security.py, ensure they are here or accessible)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


settings = Settings()

# Helper to get settings instance
def get_settings():
    return settings

