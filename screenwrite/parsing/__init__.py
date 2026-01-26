"""
Parsing module for screenwrite.

This module handles parsing markdown video scripts into structured Beat objects
with auto-generated search queries for B-roll asset fetching.
"""

from .script_parser import ScriptParser

__all__ = ['ScriptParser']
