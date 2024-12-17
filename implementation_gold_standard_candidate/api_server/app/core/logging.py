import os
import logging
import sys
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

class LogColors:
    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Log level specific colors
    DEBUG = BRIGHT_BLACK
    INFO = BRIGHT_BLUE
    WARNING = BRIGHT_YELLOW
    ERROR = BRIGHT_RED
    CRITICAL = RED
    
    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Reset
    RESET = "\033[0m"

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        original_msg = record.msg
        level_name = record.levelname
        
        if getattr(record, 'colored', False):
            if record.levelno == logging.DEBUG:
                colored_msg = f"{LogColors.DEBUG}{level_name}: {record.msg}{LogColors.RESET}"
            elif record.levelno == logging.INFO:
                colored_msg = f"{LogColors.INFO}{level_name}: {record.msg}{LogColors.RESET}"
            elif record.levelno == logging.WARNING:
                colored_msg = f"{LogColors.WARNING}{level_name}: {record.msg}{LogColors.RESET}"
            elif record.levelno == logging.ERROR:
                colored_msg = f"{LogColors.ERROR}{level_name}: {record.msg}{LogColors.RESET}"
            elif record.levelno == logging.CRITICAL:
                colored_msg = f"{LogColors.BOLD}{LogColors.CRITICAL}{level_name}: {record.msg}{LogColors.RESET}"
            else:
                colored_msg = f"{LogColors.WHITE}{level_name}: {record.msg}{LogColors.RESET}"
            record.msg = colored_msg
        
        formatted_msg = super().format(record)
        record.msg = original_msg
        return formatted_msg

def setup_logging():
    # Create logger
    if not os.path.exists(settings.LOG_FILE):
        os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # File handler (without colors)
    file_formatter = logging.Formatter(
        '%(levelname)s: %(asctime)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (with colors)
    console_formatter = ColoredFormatter(
        '%(levelname)s: %(asctime)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    # Mark console handler for colored output
    setattr(console_handler, 'colored', True)
    logger.addHandler(console_handler) 

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        status_code = response.status_code
        log_function = logging.error if status_code >= 400 else logging.info
        
        log_message = (
            f"{request.client.host} - "
            f"{status_code} {request.method} {request.url} "
            f"(completed in {process_time:.2f}s)"
        )
        log_function(log_message)
        
        return response 