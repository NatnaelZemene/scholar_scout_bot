from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Scholarship Scout Bot"
    environment: str = "dev"
    version: str = "1.0.0"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/scholar_scout"
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()