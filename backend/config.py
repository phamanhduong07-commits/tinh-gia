from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/tinh_gia_db"
    SECRET_KEY: str = "change-me-in-production-use-32-random-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 ngày
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    class Config:
        env_file = ".env"


settings = Settings()
