import os

# Secret key for sessions
SECRET_KEY = 'your-secret-key-here-change-in-production'

# Upload folder
UPLOAD_FOLDER = 'static/uploads'

# Model paths
WHISPER_MODEL = 'base'  # 'tiny', 'base', 'small', 'medium', 'large'
HUGGINGFACE_MODEL = 'facebook/bart-large-cnn'

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'adaptive_notes'

# File size limits
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB