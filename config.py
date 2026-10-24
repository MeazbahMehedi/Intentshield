"""Configuration comes from environment variables; no credentials in source."""
import os

class Config:
    SECRET_KEY = os.environ.get('PG_SECRET_KEY')
    DEBUG = False
    MAX_CONTENT_LENGTH = 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('PG_COOKIE_SECURE') == '1'
    AUTH_REQUIRED = os.environ.get('PG_AUTH_REQUIRED') == '1'
    API_TOKEN = os.environ.get('PG_API_TOKEN', '')
    RATE_LIMIT = int(os.environ.get('PG_RATE_LIMIT', '60'))
    DATABASE = os.environ.get('PG_DATABASE')
    OLLAMA_URL = os.environ.get('PG_OLLAMA_URL', 'http://127.0.0.1:11434')
    OLLAMA_MODEL = os.environ.get('PG_OLLAMA_MODEL', '')
