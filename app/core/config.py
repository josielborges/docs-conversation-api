from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    GEMINI_EMBEDDING_MODEL: str
    MASTER_API_KEY: str
    ESTANTE_USERNAME: str = ""
    ESTANTE_PASSWORD: str = ""
    
    CORS_ORIGINS: List[str] = ["*"]
    
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RAG_N_RESULTS: int = 10
    
    class Config:
        env_file = ".env"


settings = Settings()