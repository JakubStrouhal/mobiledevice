import os

class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev_key_123')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ['cs']
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

class ProductionConfig(Config):
    """Production config."""
    DEBUG = False
    TESTING = False
    # Ensure all redirects are HTTPS
    PREFERRED_URL_SCHEME = 'https'
    # Additional security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }
