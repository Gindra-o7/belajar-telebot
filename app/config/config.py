"""
Configuration module untuk aplikasi
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://stockbot:stockbot123@localhost:5432/stockbot_db"
    )
    
    # RabbitMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
    QUEUE_NAME = os.getenv("QUEUE_NAME", "telegram_updates")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Application
    APP_NAME = "Telegram Stock Bot"
    APP_VERSION = "1.0.0"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = [
            "TELEGRAM_BOT_TOKEN",
            "WEBHOOK_SECRET",
        ]
        
        missing = []
        for key in required:
            if not getattr(cls, key):
                missing.append(key)
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}\n"
                "Please check your .env file"
            )
        
        return True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"


# Select config based on environment
ENV = os.getenv("ENV", "development").lower()

if ENV == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
