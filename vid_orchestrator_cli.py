#!/usr/bin/env python3
"""
Standalone CLI script for vid-orchestrator.

This script can be run directly or used as an entry point for package installation.
"""

import sys
import os

# Add the current directory to Python path to allow importing vid_orchestrator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vid_orchestrator.cli import main

if __name__ == '__main__':
    sys.exit(main())