from pathlib import Path
import os
import tempfile

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / 'backend'
FRONTEND_DIR = BASE_DIR / 'frontend'
UPLOAD_DIR = BASE_DIR / 'uploads'
# Use the OS temp directory by default (important on Windows to avoid path length issues).
# You can override with APP_TEMP_DIR in your environment.
_default_temp_root = Path(tempfile.gettempdir()) / 'adaptive-notes'
TEMP_DIR = Path(os.getenv('APP_TEMP_DIR') or str(_default_temp_root)) / 'temp'
PDF_DIR = BASE_DIR / 'outputs' / 'pdf'
DOCX_DIR = BASE_DIR / 'outputs' / 'docx'

SECRET_KEY = os.getenv('SESSION_SECRET', os.getenv('SECRET_KEY', 'change-me'))
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', str(500 * 1024 * 1024)))
CORS_ORIGINS = os.getenv('CLIENT_ORIGIN', os.getenv('CORS_ORIGINS', '*'))
MONGODB_URI = os.getenv('MONGODB_URI', os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017'))
MONGODB_DB = os.getenv('MONGODB_DB', 'adaptive_notes')
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
PORT = int(os.getenv('PORT', '5000'))
