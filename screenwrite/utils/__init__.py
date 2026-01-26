"""
Utility modules for screenwrite.

This package contains shared utilities for error handling, validation,
and other common functionality used across the application.
"""

from .error_handling import (
    ValidationResult,
    InputValidationError,
    OutputError,
    NetworkError,
    DependencyError,
    validate_markdown_file,
    ensure_output_directory,
    retry_with_backoff,
    check_dependency,
    validate_api_key,
    handle_graceful_degradation,
    create_error_context,
    log_error_with_context
)

__all__ = [
    'ValidationResult',
    'InputValidationError',
    'OutputError',
    'NetworkError',
    'DependencyError',
    'validate_markdown_file',
    'ensure_output_directory',
    'retry_with_backoff',
    'check_dependency',
    'validate_api_key',
    'handle_graceful_degradation',
    'create_error_context',
    'log_error_with_context'
]
