import os
from pathlib import Path

class Settings:
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("Gemini_API_Key")
    MODEL: str = os.getenv("MODEL", "gemini-3.6-flash")
    
    # ChromaDB configuration
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", os.getenv("CHROMA_PATH", "chroma_db"))
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "documents")
    
    # RAG configuration
    MAX_RESULTS: int = int(os.environ.get("MAX_RESULTS", "3"))
    CONFIDENCE_THRESHOLD: float = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.5"))
    
    # Application settings
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
    DOCS_DIRECTORY: str = os.getenv("DOCS_DIRECTORY", os.path.join(os.path.dirname(__file__), "docs"))

settings = Settings()

# Print configuration on startup (useful for debugging)
if settings.DEBUG:
    print("=== Configuration ===")
    print(f"  GEMINI_API_KEY: {settings.GEMINI_API_KEY}")
    print(f"  Model: {settings.MODEL}")
    print(f"  ChromaDB: {settings.CHROMA_DB_PATH}")
    print(f"  Max Results: {settings.MAX_RESULTS}")
    print(f"  Threshold: {settings.CONFIDENCE_THRESHOLD}")
    print(f"  Debug: {settings.DEBUG}")
    print(f" Gemini key: {'set' if settings.GEMINI_API_KEY else 'not set'}")
