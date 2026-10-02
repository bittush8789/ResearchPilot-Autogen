import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    app_path = ROOT_DIR / "frontend" / "app.py"
    print(f"Launching ResearchPilot Streamlit Frontend from {app_path}...")
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", "8501", "--server.headless", "true"]
    subprocess.run(cmd)
