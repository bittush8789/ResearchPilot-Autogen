"""
ResearchPilot — Unified Application CLI & Runner
Usage:
    python run.py            # Starts both FastAPI Backend and Streamlit Frontend
    python run.py backend    # Starts only the FastAPI Backend (Port 8000)
    python run.py frontend   # Starts only the Streamlit Frontend (Port 8501)
    python run.py test       # Runs the automated pytest test suite
"""

import sys
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def run_backend():
    print("[+] Launching FastAPI Backend on http://127.0.0.1:8000...")
    cmd = [sys.executable, str(ROOT_DIR / "scripts" / "run_backend.py")]
    return subprocess.Popen(cmd)

def run_frontend():
    print("[+] Launching Streamlit Frontend on http://localhost:8501...")
    cmd = [sys.executable, str(ROOT_DIR / "scripts" / "run_frontend.py")]
    return subprocess.Popen(cmd)

def run_tests():
    print("[+] Running automated test suite...")
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    subprocess.run(cmd)

def run_all():
    print("=" * 64)
    print("  ⚡ ResearchPilot — Multi-Agent Research Platform")
    print("=" * 64)
    
    backend_proc = run_backend()
    time.sleep(2)
    frontend_proc = run_frontend()

    print("\n✓ Services Online:")
    print("  • Web UI:      http://localhost:8501")
    print("  • Backend API: http://127.0.0.1:8000")
    print("  • API Docs:    http://127.0.0.1:8000/docs\n")
    print("Press Ctrl+C to terminate both servers.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down ResearchPilot services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    
    if arg == "backend":
        proc = run_backend()
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
    elif arg == "frontend":
        proc = run_frontend()
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
    elif arg == "test":
        run_tests()
    else:
        run_all()
