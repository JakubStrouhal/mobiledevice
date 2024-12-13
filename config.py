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
    # Enhanced security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    # Additional security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
    }
