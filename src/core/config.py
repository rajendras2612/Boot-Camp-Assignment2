from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field("multimodal-rag", env="APP_NAME")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")
    openai_completion_model: str = Field("gpt-4o-mini", env="OPENAI_COMPLETION_MODEL")
    openai_embedding_model: str = Field("text-embedding-3-large", env="OPENAI_EMBEDDING_MODEL")
    local_embedding_model: str = Field("all-MiniLM-L6-v2", env="LOCAL_EMBEDDING_MODEL")

    pdf_storage_path: Path = Field(Path("./data/pdf"), env="PDF_STORAGE_PATH")
    vector_store_path: Path = Field(Path("./data/vector_store"), env="VECTOR_STORE_PATH")

    chunk_size: int = Field(800, env="CHUNK_SIZE")
    chunk_overlap: int = Field(100, env="CHUNK_OVERLAP")
    top_k: int = Field(5, env="TOP_K")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
