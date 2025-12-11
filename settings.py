import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    MONGO_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/grading_system'

    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # OpenAI settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'

    # Plagiarism threshold
    PLAGIARISM_THRESHOLD = 0.91

    # CDN Configuration (Quick Win for Performance)
    CDN_DOMAIN = os.environ.get('CDN_DOMAIN', '')
    CDN_HTTPS = os.environ.get('CDN_HTTPS', 'true').lower() == 'true'
    STATIC_URL = f"https://{CDN_DOMAIN}" if CDN_DOMAIN else "/static"

    # Performance settings
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files

    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
