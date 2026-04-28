import os
from pydantic_settings import BaseSettings

# Tìm file .env kể cả khi chạy từ thư mục con
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_env_path = os.path.join(_root, ".env")


class Settings(BaseSettings):
    # Mặc định SQLite — không cần cài PostgreSQL
    DATABASE_URL: str = f"sqlite:///{os.path.join(_root, 'tinh_gia.db')}"
    SECRET_KEY: str = "nam-phuong-secret-key-doi-lai-truoc-khi-deploy"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 ngày
    ALLOWED_ORIGINS: str = "*"

    class Config:
        env_file = _env_path


settings = Settings()
