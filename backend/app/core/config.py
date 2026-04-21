from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./hre.db"
    # Dify 默认配置（可选，优先使用 UnitRuntimeConfig 中的动态配置）
    DIFY_API_URL: str = "http://localhost:80"
    DIFY_API_KEY: str = ""
    DIFY_MOCK_MODE: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()