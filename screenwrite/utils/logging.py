"""
Centralized logging configuration for screenwrite.

This module provides a single place to configure logging across the entire
application, ensuring consistent behavior and reducing duplication.
"""

import logging
import time
from contextlib import contextmanager
from typing import Optional
from pathlib import Path


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        verbose: Enable DEBUG level logging if True, otherwise INFO
        log_file: Optional path to write logs to a file
    """
    # Determine logging level
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers to avoid duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if log file specified
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(logging.DEBUG)  # File always gets DEBUG level
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            root_logger.warning(f"Failed to setup file logging to {log_file}: {e}")
    
    # Reduce noise from external libraries in non-verbose mode
    if not verbose:
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('yt_dlp').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.
    
    This is a convenience wrapper around logging.getLogger().
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


@contextmanager
def log_operation(operation_name: str, logger: Optional[logging.Logger] = None, 
                  log_level: int = logging.INFO):
    """
    Context manager for logging the duration of an operation.
    
    Logs when operation starts and ends, including elapsed time.
    Useful for measuring performance of components.
    
    Args:
        operation_name: Name of the operation being timed
        logger: Logger instance (uses root logger if not provided)
        log_level: Logging level to use (default: INFO)
        
    Example:
        with log_operation("Parse script", logger=logger):
            beats = parser.parse(script_path)
            
        # Output:
        # [START] Parse script
        # [END] Parse script - 1.23s
    """
    if logger is None:
        logger = logging.getLogger()
    
    start_time = time.time()
    logger.log(log_level, f"[START] {operation_name}")
    
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        logger.log(log_level, f"[END] {operation_name} - {elapsed:.2f}s")

