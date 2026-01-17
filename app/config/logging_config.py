"""
Konfigurasi logging untuk aplikasi
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging(name: str = "stockbot", log_level: str = "INFO"):
    """
    Setup logging configuration
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Create logs directory if not exists
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Get log level from environment or parameter
    level = os.getenv("LOG_LEVEL", log_level).upper()
    log_level_obj = getattr(logging, level, logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level_obj)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_obj)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        f"{log_dir}/{name}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level_obj)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error File Handler (separate file for errors)
    error_handler = RotatingFileHandler(
        f"{log_dir}/{name}_error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


# Default logger
logger = setup_logging()
