"""
Configuration module loader for environment variables.
"""
import os

# Configuration settings


class Settings:
    def __init__(self):
        self.PROJECT_NAME = "ArenaSync AI"
        self.VERSION = "1.0.0"
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.STADIUM_NAME = os.getenv("STADIUM_NAME", "MetLife Stadium (New York/New Jersey)")
        self.HOST = os.getenv("HOST", "127.0.0.1")
        self.PORT = int(os.getenv("PORT", "8000"))
        # Security controls
        self.RATE_LIMIT_PER_MINUTE = 60
        # AI models
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

settings = Settings()
