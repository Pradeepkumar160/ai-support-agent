from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""  # kept optional for FAQ embeddings fallback
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/support_ai"
    REDIS_URL: str = "redis://redis:6379"
    JWT_SECRET: str = "change-this-secret"
    MODEL_NAME: str = "llama-3.3-70b-versatile"  # best free Groq model

    class Config:
        env_file = ".env"


settings = Settings()
