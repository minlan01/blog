from functools import cached_property
import secrets
import warnings

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "赤夜冥岚的编程小屋 API"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://127.0.0.1:3710,http://localhost:3710"
    DATABASE_BACKEND: str = "sqlite"
    SQLITE_DB_PATH: str = "blog.db"
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "blog"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "blog"
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    LLM_DEFAULT_MODEL: str = "deepseek-v4-flash"
    LLM_TIMEOUT: int = 120
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # SMTP Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@blog.com"
    FRONTEND_URL: str = "http://localhost:3710"

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/github/callback"

    # Upload
    MAX_UPLOAD_SIZE_MB: int = 1024
    UPLOAD_ALLOWED_TYPES: str = (
        "image/png,image/jpeg,image/gif,image/webp,image/svg+xml,"
        "video/mp4,video/webm,video/quicktime,video/x-matroska,"
        "audio/mpeg,audio/mp3,audio/wav,audio/x-wav,audio/aac,audio/mp4,audio/x-m4a,audio/ogg,audio/webm"
    )

    # Object storage
    STORAGE_BACKEND: str = "local"
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minlan01"
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET: str = "blog-media"
    MINIO_SECURE: bool = False

    # Environment
    ENV: str = "production"  # "production" | "development" | "test"

    # Site URL (for sitemap, canonical, OG meta)
    SITE_URL: str = "http://localhost:3710"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @cached_property
    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]

    @property
    def cors_is_secure(self) -> bool:
        """生产环境 CORS 安全检查：不应包含通配符或 localhost"""
        origins = self.cors_origins_list
        if not origins or "*" in origins:
            return False
        for o in origins:
            low = o.lower()
            if "localhost" in low or "127.0.0.1" in low or "0.0.0.0" in low:
                return False
            if not low.startswith("https://"):
                return False
        return True

    @cached_property
    def database_url(self) -> str:
        if self.DATABASE_BACKEND.lower() == "sqlite":
            return f"sqlite:///{self.SQLITE_DB_PATH}"
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    @cached_property
    def upload_allowed_types_list(self) -> list[str]:
        return [t.strip() for t in self.UPLOAD_ALLOWED_TYPES.split(",") if t.strip()]

    @cached_property
    def llm_api_key(self) -> str:
        return self.LLM_API_KEY or self.DEEPSEEK_API_KEY

    @cached_property
    def llm_base_url(self) -> str:
        return self.LLM_BASE_URL.rstrip("/")

    @cached_property
    def use_minio(self) -> bool:
        return self.STORAGE_BACKEND.lower() == "minio"


settings = Settings()

if not settings.SECRET_KEY:
    if settings.DATABASE_BACKEND.lower() == "sqlite" and settings.SQLITE_DB_PATH == ":memory:":
        settings.SECRET_KEY = secrets.token_hex(32)
        warnings.warn("SECRET_KEY not set — using random key for tests. Set SECRET_KEY in .env for production.")
    else:
        raise ValueError(
            "SECRET_KEY is not set. "
            "Please add SECRET_KEY=<your-secret> to your .env file. "
            "You can generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

# 生产环境 CORS 安全校验
if settings.ENV == "production" and not settings.cors_is_secure:
    warnings.warn(
        f"[Security] 生产环境 CORS_ORIGINS 不安全: {settings.CORS_ORIGINS}. "
        "应只包含 https:// 开头的生产域名，不包含 localhost/通配符。"
    )
