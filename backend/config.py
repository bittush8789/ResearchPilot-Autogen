import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env", override=True)

class Settings:
    PROJECT_NAME: str = "ResearchPilot"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Multi-Agent Research Intelligence Platform"
    
    # Host & Port
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    BACKEND_URL: str = os.getenv("BACKEND_URL", f"http://{HOST}:{PORT}")
    
    # Groq Configuration: Exclusively GPT-OSS 120B (Medium)
    @property
    def GROQ_API_KEY(self) -> str:
        return os.getenv("GROQ_API_KEY", "").strip()

    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_MODEL_DISPLAY_NAME: str = "GPT-OSS 120B (Medium)"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    
    # Supported Groq Model: Exclusively locked to GPT-OSS 120B
    AVAILABLE_MODELS = [
        "openai/gpt-oss-120b"
    ]
    
    # Research Parameters
    DEFAULT_MAX_PAPERS: int = int(os.getenv("DEFAULT_MAX_PAPERS", "5"))
    DOWNLOAD_PDFS: bool = os.getenv("DOWNLOAD_PDFS", "true").lower() in ("true", "1", "yes")
    
    # Storage
    STORAGE_DIR: Path = ROOT_DIR / "data"
    SESSIONS_DIR: Path = STORAGE_DIR / "sessions"
    PDFS_DIR: Path = STORAGE_DIR / "pdfs"

settings = Settings()
settings.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
settings.PDFS_DIR.mkdir(parents=True, exist_ok=True)
