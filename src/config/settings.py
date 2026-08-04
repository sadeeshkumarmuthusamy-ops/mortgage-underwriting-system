from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "mortgage-underwriting-api"
    
    # LLM Provider Configuration
    # Supports "openai", "anthropic", etc.
    GROQ_LLM_PROVIDER: str = Field(default="groq", env="GROQ_LLM_PROVIDER")
    GROQ_LLM_MODEL: str = Field(default="llama-3.1-8b-instant", env="GROQ_LLM_MODEL")
    GROQ_LLM_TEMPERATURE: float = Field(default=0.0, env="GROQ_LLM_TEMPERATURE")
    OPENAI_LLM_PROVIDER: str = Field(default="openai", env="OPENAI_LLM_PROVIDER")
    OPENAI_LLM_MODEL: str = Field(default="gpt-4o-mini", env="OPENAI_LLM_MODEL")
    OPENAI_LLM_TEMPERATURE: float = Field(default=0.0, env="OPENAI_LLM_TEMPERATURE")
    
    # API Keys
    GROQ_API_KEY: str | None = Field(default=None, env="GROQ_API_KEY")
    ANTHROPIC_API_KEY: str | None = Field(default=None, env="ANTHROPIC_API_KEY")
    OPENAI_API_KEY: str | None = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_API_BASE: str | None = Field(default=None, env="OPENAI_API_BASE")
    TAVILY_API_KEY: str | None = Field(default=None, env="TAVILY_API_KEY")
    CHROMA_DB_PATH: str | None = Field(default=None, env="CHROMA_DB_PATH")
    PDF_PATH: str | None = Field(default=None, env="PDF_PATH")

    CHUNK_SIZE: int = Field(default=1000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")

    class Config:
        env_file = ".env"
        extra = "ignore"

# Global settings instance
settings = Settings()