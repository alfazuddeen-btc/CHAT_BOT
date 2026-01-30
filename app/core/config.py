import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    APP_NAME: str = os.getenv("APP_NAME", "Cardiac RAG Chatbot")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", 384))

    TOP_K: int = int(os.getenv("TOP_K", 5))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", 0.7))

    ALLOW_GENERAL_MEDICAL_INFO: bool = os.getenv("ALLOW_GENERAL_MEDICAL_INFO", "True").lower() == "true"
    ALLOW_DIAGNOSIS: bool = os.getenv("ALLOW_DIAGNOSIS", "False").lower() == "true"
    ALLOW_PRESCRIPTION: bool = os.getenv("ALLOW_PRESCRIPTION", "False").lower() == "true"

settings = Settings()