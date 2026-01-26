"""
Main entry point for screenwrite when run as a module.

This allows the package to be executed with:
    python -m screenwrite
"""

from .cli import main

if __name__ == '__main__':
    exit(main())
