import os
from pathlib import Path

basedir = Path(__file__).resolve().parent.parent

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + str(basedir / 'instance' / 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pagination configuration
    POSTS_PER_PAGE = 20
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = basedir / 'static' / 'images' / 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB
    
    # Markdown configuration
    MARKDOWN_EXTENSIONS = ['codehilite', 'fenced_code', 'tables', 'nl2br']


