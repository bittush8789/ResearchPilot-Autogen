import sys
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from backend.config import settings

if __name__ == "__main__":
    print(f"Starting ResearchPilot FastAPI Backend on {settings.HOST}:{settings.PORT}...")
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    )
