"""
Main entry point for vid-orchestrator when run as a module.

This allows the package to be executed with:
    python -m vid_orchestrator
"""

from .cli import main

if __name__ == '__main__':
    exit(main())