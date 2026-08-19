from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "YeYi Blog API"
    DEBUG: bool = False

    DATABASE_URL: str = "mysql+asyncmy://root:root@localhost:3306/yeyi_blog"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "https://blog.yeyeyiyi.online", "https://admin.yeyeyiyi.online"]
    SITE_URL: str = "http://localhost:3000"

    MCP_API_KEY: str = ""
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8100
    MCP_RATE_LIMIT: int = 120
    MCP_RATE_WINDOW: int = 60
    MCP_REQUIRE_API_KEY: bool = True
    MCP_ALLOWED_HOSTS: list[str] = []
    MCP_ALLOWED_ORIGINS: list[str] = []
    MCP_PUBLIC_URL: str = "https://blogmcp.yeyeyiyi.online/mcp"
    MCP_SETTINGS_ENCRYPTION_KEY: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
