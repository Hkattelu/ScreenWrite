"""
ScreenWrite: CLI tool for automating video timeline creation from markdown scripts.

This package orchestrates the conversion of markdown video scripts into DaVinci Resolve-compatible 
FCPXML timelines with auto-fetched B-roll ScreenWrite.
"""

__version__ = "0.1.0"

# Main components
from .orchestrator import VideoOrchestrator
from .core.beat import Beat
from .parsing.script_parser import ScriptParser
from .fetchers.asset_orchestrator import AssetOrchestrator
from .generators.xml_generator import XMLGenerator

# CLI interface
from .cli import main as cli_main

# Optional components
try:
    from .resolve_integration import ResolveIntegration
except ImportError:
    ResolveIntegration = None

__all__ = [
    'VideoOrchestrator',
    'Beat',
    'ScriptParser', 
    'AssetOrchestrator',
    'XMLGenerator',
    'ResolveIntegration',
    'cli_main'
]
