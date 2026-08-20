#!/usr/bin/env python3
"""
Root entrypoint for NexusDev AI backend.
Allows running 'python main.py' or 'python3 main.py' directly from project root.
"""

import sys
from pathlib import Path

# Add backend directory to Python path
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    print("🚀 Launching NexusDev AI Control Center & API Server on http://localhost:8000 ...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
