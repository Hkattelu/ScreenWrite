"""
Comprehensive error handling utilities for vid-orchestrator.

This module provides centralized error handling, validation, and retry logic
to ensure graceful degradation and clear error messages throughout the system.
"""

import os
import time
import logging
import functools
from pathlib import Path
from typing import Optional, Callable, Any, Dict, List, Union
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class InputValidationError(Exception):
    """Raised when input validation fails."""
    pass


class OutputError(Exception):
    """Raised when output operations fail."""
    pass


class NetworkError(Exception):
    """Raised when network operations fail."""
    pass


class DependencyError(Exception):
    """Raised when required dependencies are missing."""
    pass


def validate_markdown_file(file_path: str) -> ValidationResult:
    """
    Validate a markdown script file for processing.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        ValidationResult with validation status and messages
    """
    result = ValidationResult(is_valid=False)
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            result.error_message = f"Script file not found: {file_path}"
            return result
        
        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            result.error_message = f"Path is not a file: {file_path}"
            return result
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            result.error_message = f"Cannot read script file: {file_path} (check permissions)"
            return result
        
        # Check file extension
        script_path = Path(file_path)
        valid_extensions = ['.md', '.markdown', '.txt']
        if script_path.suffix.lower() not in valid_extensions:
            result.warnings.append(
                f"File '{file_path}' does not have a markdown extension "
                f"({', '.join(valid_extensions)}). Proceeding anyway."
            )
        
        # Check file size (reasonable limits)
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            result.error_message = f"Script file is empty: {file_path}"
            return result
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            result.warnings.append(
                f"Script file is very large ({file_size / 1024 / 1024:.1f}MB). "
                "Processing may be slow."
            )
        
        # Try to read and validate content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            content = None
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    result.warnings.append(
                        f"File encoding detected as {encoding} instead of UTF-8"
                    )
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                result.error_message = f"Cannot decode file content: {file_path} (unsupported encoding)"
                return result
        
        # Validate content is not empty after stripping whitespace
        if not content.strip():
            result.error_message = f"Script file contains no content: {file_path}"
            return result
        
        # Check for basic markdown structure
        lines = content.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if len(non_empty_lines) < 2:
            result.warnings.append(
                "Script file has very little content. Ensure it contains enough text for meaningful beats."
            )
        
        # Check for potential markdown syntax issues
        has_headers = any(line.startswith('#') for line in non_empty_lines)
        if not has_headers:
            result.warnings.append(
                "No markdown headers found. Consider adding headers (# or ##) for better context."
            )
        
        # Estimate word count for duration validation
        word_count = len(content.split())
        estimated_duration = word_count / 2.5  # 2.5 words per second heuristic
        
        if estimated_duration < 5:
            result.warnings.append(
                f"Script is very short (~{estimated_duration:.1f}s estimated). "
                "May not generate valid beats (5-10s each)."
            )
        
        if estimated_duration > 600:  # 10 minutes
            result.warnings.append(
                f"Script is very long (~{estimated_duration/60:.1f}min estimated). "
                "Processing may take significant time."
            )
        
        result.is_valid = True
        return result
        
    except Exception as e:
        result.error_message = f"Unexpected error validating script file: {e}"
        return result


def ensure_output_directory(output_path: str) -> ValidationResult:
    """
    Ensure output directory exists and is writable.
    
    Args:
        output_path: Path to the output file
        
    Returns:
        ValidationResult with operation status and messages
    """
    result = ValidationResult(is_valid=False)
    
    try:
        output_file = Path(output_path)
        output_dir = output_file.parent
        
        # Check if output directory exists
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")
                result.warnings.append(f"Created output directory: {output_dir}")
            except PermissionError:
                result.error_message = (
                    f"Cannot create output directory: {output_dir} "
                    "(permission denied)"
                )
                return result
            except Exception as e:
                result.error_message = f"Failed to create output directory: {output_dir} ({e})"
                return result
        
        # Check if output directory is actually a directory
        if not output_dir.is_dir():
            result.error_message = f"Output directory path exists but is not a directory: {output_dir}"
            return result
        
        # Check if output directory is writable
        if not os.access(output_dir, os.W_OK):
            result.error_message = f"Cannot write to output directory: {output_dir} (permission denied)"
            return result
        
        # Check if output file already exists and is writable
        if output_file.exists():
            if not os.access(output_file, os.W_OK):
                result.error_message = f"Cannot overwrite existing output file: {output_path} (permission denied)"
                return result
            result.warnings.append(f"Will overwrite existing file: {output_path}")
        
        # Check available disk space (warn if less than 100MB)
        try:
            import shutil
            free_space = shutil.disk_usage(output_dir).free
            if free_space < 100 * 1024 * 1024:  # 100MB
                result.warnings.append(
                    f"Low disk space in output directory: {free_space / 1024 / 1024:.1f}MB available"
                )
        except Exception:
            # Ignore disk space check errors
            pass
        
        result.is_valid = True
        return result
        
    except Exception as e:
        result.error_message = f"Unexpected error checking output directory: {e}"
        return result


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Final attempt failed
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise e
                    
                    # Log retry attempt
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    
                    # Wait before retry
                    time.sleep(delay)
                    
                    # Increase delay for next attempt
                    delay = min(delay * backoff_factor, max_delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def check_dependency(
    command: str,
    name: str = None,
    version_flag: str = "--version",
    timeout: float = 10.0
) -> ValidationResult:
    """
    Check if a system dependency is available.
    
    Args:
        command: Command to check (e.g., 'ffmpeg', 'python')
        name: Human-readable name for the dependency
        version_flag: Flag to get version info
        timeout: Timeout for the command in seconds
        
    Returns:
        ValidationResult indicating if dependency is available
    """
    result = ValidationResult(is_valid=False)
    dep_name = name or command
    
    try:
        import subprocess
        
        # Try to run the command with version flag
        process = subprocess.run(
            [command, version_flag],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if process.returncode == 0:
            result.is_valid = True
            # Extract version info if available
            version_output = process.stdout.strip() or process.stderr.strip()
            if version_output:
                first_line = version_output.split('\n')[0]
                logger.debug(f"{dep_name} available: {first_line}")
        else:
            result.error_message = f"{dep_name} command failed with return code {process.returncode}"
            
    except subprocess.TimeoutExpired:
        result.error_message = f"{dep_name} command timed out after {timeout}s"
    except FileNotFoundError:
        result.error_message = f"{dep_name} not found in system PATH"
    except Exception as e:
        result.error_message = f"Error checking {dep_name}: {e}"
    
    return result


def validate_api_key(api_key: str, service_name: str) -> ValidationResult:
    """
    Validate an API key format.
    
    Args:
        api_key: The API key to validate
        service_name: Name of the service (for error messages)
        
    Returns:
        ValidationResult indicating if API key appears valid
    """
    result = ValidationResult(is_valid=False)
    
    if not api_key:
        result.error_message = f"No {service_name} API key provided"
        return result
    
    if not isinstance(api_key, str):
        result.error_message = f"{service_name} API key must be a string"
        return result
    
    # Basic format validation
    api_key = api_key.strip()
    
    if len(api_key) < 10:
        result.error_message = f"{service_name} API key appears too short (less than 10 characters)"
        return result
    
    if len(api_key) > 200:
        result.error_message = f"{service_name} API key appears too long (more than 200 characters)"
        return result
    
    # Check for common issues
    if api_key.startswith('your_') or api_key.startswith('YOUR_'):
        result.error_message = f"{service_name} API key appears to be a placeholder"
        return result
    
    if ' ' in api_key:
        result.warnings.append(f"{service_name} API key contains spaces - this may cause issues")
    
    result.is_valid = True
    return result


def handle_graceful_degradation(
    operation_name: str,
    error: Exception,
    fallback_value: Any = None,
    continue_processing: bool = True
) -> Any:
    """
    Handle graceful degradation when operations fail.
    
    Args:
        operation_name: Name of the operation that failed
        error: The exception that occurred
        fallback_value: Value to return if operation fails
        continue_processing: Whether to continue processing or raise
        
    Returns:
        Fallback value if continue_processing is True
        
    Raises:
        The original exception if continue_processing is False
    """
    error_msg = f"{operation_name} failed: {error}"
    
    if continue_processing:
        logger.warning(f"{error_msg}. Continuing with graceful degradation.")
        return fallback_value
    else:
        logger.error(error_msg)
        raise error


def create_error_context(
    operation: str,
    component: str = None,
    **context_data
) -> Dict[str, Any]:
    """
    Create standardized error context for logging and debugging.
    
    Args:
        operation: The operation being performed
        component: The component where the error occurred
        **context_data: Additional context information
        
    Returns:
        Dictionary with error context
    """
    context = {
        'operation': operation,
        'timestamp': time.time(),
        **context_data
    }
    
    if component:
        context['component'] = component
    
    return context


def log_error_with_context(
    logger_instance: logging.Logger,
    level: int,
    message: str,
    error: Exception = None,
    **context
):
    """
    Log an error with structured context information.
    
    Args:
        logger_instance: Logger to use
        level: Logging level (e.g., logging.ERROR)
        message: Error message
        error: Exception object (optional)
        **context: Additional context information
    """
    # Build context string
    context_parts = []
    for key, value in context.items():
        context_parts.append(f"{key}={value}")
    
    context_str = f" [{', '.join(context_parts)}]" if context_parts else ""
    
    # Add exception info if provided
    if error:
        full_message = f"{message}: {error}{context_str}"
        logger_instance.log(level, full_message, exc_info=True)
    else:
        full_message = f"{message}{context_str}"
        logger_instance.log(level, full_message)