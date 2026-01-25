"""
Beat caching utilities for faster re-runs with identical scripts.

This module provides functionality to cache parsed beats based on script content,
enabling faster processing when the same script is processed multiple times.
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Optional, List
from dataclasses import asdict

from ..core.beat import Beat


def _get_file_hash(file_path: str) -> str:
    """
    Calculate MD5 hash of a file for cache key generation.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 hash of file contents
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _get_cache_dir() -> Path:
    """Get the cache directory, creating if necessary."""
    cache_dir = Path.home() / ".cache" / "vid_orchestrator"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def cache_beats(file_path: str, beats: List[Beat], 
                max_age_hours: int = 24) -> None:
    """
    Cache parsed beats to disk.
    
    Args:
        file_path: Path to the markdown script file
        beats: List of Beat objects to cache
        max_age_hours: Cache validity period in hours (default: 24)
    """
    try:
        file_hash = _get_file_hash(file_path)
        cache_dir = _get_cache_dir()
        cache_file = cache_dir / f"{file_hash}.json"
        
        # Convert beats to serializable format
        beats_data = []
        for beat in beats:
            beat_dict = {
                'id': beat.id,
                'text': beat.text,
                'stock_keyword': beat.stock_keyword,
                'youtube_search_phrase': beat.youtube_search_phrase,
                'duration': beat.duration,
                'asset_paths': beat.asset_paths
            }
            beats_data.append(beat_dict)
        
        cache_data = {
            'file_hash': file_hash,
            'timestamp': time.time(),
            'max_age_hours': max_age_hours,
            'beats': beats_data
        }
        
        cache_file.write_text(json.dumps(cache_data, indent=2))
    except Exception as e:
        # Fail silently - caching is optional
        pass


def load_cached_beats(file_path: str, max_age_hours: int = 24) -> Optional[List[Beat]]:
    """
    Load beats from cache if available and valid.
    
    Args:
        file_path: Path to the markdown script file
        max_age_hours: Only return cache if younger than this (default: 24)
        
    Returns:
        List of cached Beat objects, or None if cache unavailable/invalid
    """
    try:
        file_hash = _get_file_hash(file_path)
        cache_dir = _get_cache_dir()
        cache_file = cache_dir / f"{file_hash}.json"
        
        if not cache_file.exists():
            return None
        
        # Check cache age
        cache_age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
        if cache_age_hours > max_age_hours:
            return None
        
        # Load and parse cache
        cache_data = json.loads(cache_file.read_text())
        
        # Reconstruct Beat objects
        beats = []
        for beat_dict in cache_data['beats']:
            beat = Beat(
                id=beat_dict['id'],
                text=beat_dict['text'],
                stock_keyword=beat_dict['stock_keyword'],
                youtube_search_phrase=beat_dict['youtube_search_phrase']
            )
            # Restore asset_paths if they were cached
            if 'asset_paths' in beat_dict:
                beat.asset_paths = beat_dict['asset_paths']
            beats.append(beat)
        
        return beats
    except Exception:
        # Return None if any error occurs during cache loading
        return None


def clear_cache() -> None:
    """Clear all cached beats."""
    try:
        cache_dir = _get_cache_dir()
        for cache_file in cache_dir.glob("*.json"):
            cache_file.unlink()
    except Exception:
        # Fail silently
        pass


def get_cache_size() -> int:
    """
    Get total size of cache in bytes.
    
    Returns:
        Total cache size in bytes
    """
    try:
        cache_dir = _get_cache_dir()
        return sum(f.stat().st_size for f in cache_dir.glob("*.json"))
    except Exception:
        return 0
