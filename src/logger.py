import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


class CustomFormatter(logging.Formatter):
    
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(
    name: str = "app",
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: Optional[str] = None
) -> logging.Logger:
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
    console_formatter = CustomFormatter(
        '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
    
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    if log_to_file:
        if log_dir is None:
            project_root = Path(__file__).parent.parent
            log_dir_path = project_root / "logs"
        else:
            log_dir_path = Path(log_dir)
        
        log_dir_path.mkdir(exist_ok=True)
        
        log_file = log_dir_path / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"app.{name}")
    return logging.getLogger("app")


class AppError(Exception):
    pass


class WindowManagerError(AppError):
    pass


class SearchEngineError(AppError):
    pass


class HotkeyError(AppError):
    pass


class UIError(AppError):
    pass


def log_exception(logger: logging.Logger, exception: Exception, context: str = "") -> None:
    context_str = f" [{context}]" if context else ""
    logger.error(f"Exception{context_str}: {type(exception).__name__}: {exception}", exc_info=True)


main_logger = setup_logging()