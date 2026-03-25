from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    api_key: str = "dev-api-key-change-in-production"

    # Database
    database_url: str = "postgresql://localhost:5432/image_to_excel"

    # File upload limits
    max_file_size_mb: int = 20

    # Supported file types
    supported_file_types: list[str] = ["pdf", "jpeg", "jpg", "png"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
