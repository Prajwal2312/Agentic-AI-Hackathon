import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file from backend root or workspace root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
REMEDIATED_DIR = STORAGE_DIR / "remediated"
REPORTS_DIR = STORAGE_DIR / "reports"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"

# Create directories if they do not exist
for d in [STORAGE_DIR, UPLOADS_DIR, REMEDIATED_DIR, REPORTS_DIR, SAMPLE_DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    APP_NAME: str = "PRIVESCAN AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{STORAGE_DIR}/privescan.db")
    
    # Gemini AI configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    
    # Confidence thresholds
    CONFIRMATION_THRESHOLD: float = 0.85
    AMBIGUOUS_THRESHOLD: float = 0.50
    
    # File limits
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".xlsx", ".csv", ".txt", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}

settings = Settings()
