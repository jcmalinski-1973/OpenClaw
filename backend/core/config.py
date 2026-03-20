from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Banco de dados
    DATABASE_URL: str = "postgresql+psycopg2://pedidobk:pedidobk2026@localhost:5432/pedidobk"

    # GCS
    GCS_BUCKET_NAME: str = "financeiro-00-bucket"
    GCS_PROJECT_ID: str = "financeiro-489122"
    GCS_PREFIX: str = "pedidos"

    # Storage backend: "gcs" (produção) | "local" (desenvolvimento)
    STORAGE_BACKEND: str = "gcs"
    LOCAL_STORAGE_DIR: str = "/tmp/pedidobk-storage"

    # App
    APP_ENV: str = "production"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
