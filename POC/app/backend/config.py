"""Backend Configuration"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

DEBUG = os.getenv("DEBUG", "True") == "True"
API_PORT = int(os.getenv("API_PORT", "8000"))
UPLOAD_DIR = str(BASE_DIR / "uploads")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
MAX_FILE_SIZE_MB = 100

# Ensure uploads directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
