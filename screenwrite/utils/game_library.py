"""
Persistent per-game footage library.

A game's chapter index and downloaded clips are fetched ONCE and reused
across every essay on that game - YouTube actively fights downloads, so the
war is fought once per game, not once per run. Layout (per game, under
~/.cache/screenwrite/games/<slug>/):

    chapter_index.json   cached source-video/chapter index (TTL'd)
    manifest.json        clips keyed "<video_id>@<start>+<window>" +
                         per-video download success stats
    clips/               the clip files themselves

JSON, fail-silent, same conventions as utils/cache.py. Manifest writes are
lock-guarded (fetching runs in a thread pool).
"""

import json
import logging
import re
import shutil
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Chapter indexes go stale slowly (new walkthroughs appear, old ones die).
CHAPTER_INDEX_TTL_HOURS = 168

_SCHEMA_VERSION = 1


def _slug(game: str) -> str:
    tokens = re.findall(r'[a-z0-9]+', (game or '').lower())
    return '-'.join(tokens) or 'unknown-game'


def default_library_root() -> Path:
    return Path.home() / '.cache' / 'screenwrite' / 'games'


class GameLibrary:
    """Disk-backed clip + chapter-index cache for one game."""

    def __init__(self, game: str, root: Optional[Path] = None):
        """
        Args:
            game: Game title (slugged into the directory name).
            root: Library root override (injectable for tests).
        """
        self.game = game
        self.dir = (root or default_library_root()) / _slug(game)
        self.clips_dir = self.dir / 'clips'
        self._lock = threading.Lock()
        try:
            self.clips_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning(f"Game library unavailable at {self.dir}: {e}")

    # ------------------------------------------------------------------
    # Manifest plumbing
    # ------------------------------------------------------------------

    @property
    def _manifest_path(self) -> Path:
        return self.dir / 'manifest.json'

    def _load_manifest(self) -> Dict[str, Any]:
        try:
            data = json.loads(self._manifest_path.read_text(encoding='utf-8'))
            if data.get('schema_version') == _SCHEMA_VERSION:
                return data
        except (OSError, ValueError):
            pass
        return {'schema_version': _SCHEMA_VERSION, 'clips': {}, 'source_stats': {}}

    def _save_manifest(self, manifest: Dict[str, Any]) -> None:
        try:
            self._manifest_path.write_text(
                json.dumps(manifest, indent=2), encoding='utf-8'
            )
        except OSError as e:
            logger.debug(f"Could not write game library manifest: {e}")

    @staticmethod
    def clip_key(video_id: str, segment_start: float, window: float) -> str:
        """Same key format the chaptered fetcher's in-memory cache uses."""
        return f"{video_id}@{int(segment_start)}+{int(window)}"

    # ------------------------------------------------------------------
    # Chapter index
    # ------------------------------------------------------------------

    def load_chapter_index(
        self, ttl_hours: int = CHAPTER_INDEX_TTL_HOURS
    ) -> Optional[List[dict]]:
        """Return the cached chapter index, or None if absent/stale."""
        path = self.dir / 'chapter_index.json'
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        if data.get('schema_version') != _SCHEMA_VERSION:
            return None
        age_hours = (time.time() - data.get('built_at', 0)) / 3600
        if age_hours > ttl_hours:
            return None
        sources = data.get('sources')
        if not isinstance(sources, list):
            return None
        logger.info(
            f"Chapter index for '{self.game}' loaded from library "
            f"({len(sources)} sources, {age_hours:.0f}h old)"
        )
        return sources

    def save_chapter_index(self, index: List[dict]) -> None:
        """Persist a freshly built chapter index."""
        try:
            (self.dir / 'chapter_index.json').write_text(
                json.dumps({
                    'schema_version': _SCHEMA_VERSION,
                    'game': self.game,
                    'built_at': time.time(),
                    'sources': index,
                }, indent=2),
                encoding='utf-8',
            )
        except OSError as e:
            logger.debug(f"Could not cache chapter index: {e}")

    # ------------------------------------------------------------------
    # Clips
    # ------------------------------------------------------------------

    def find_clip(self, video_id: str, segment_start: float, window: float) -> Optional[str]:
        """Return the library path for a clip if present on disk."""
        with self._lock:
            entry = self._load_manifest()['clips'].get(
                self.clip_key(video_id, segment_start, window)
            )
        if not entry:
            return None
        path = entry.get('path')
        if path and Path(path).exists():
            return path
        return None

    def store_clip(self, path: str, video_id: str,
                   segment_start: float, window: float) -> str:
        """
        Copy a downloaded clip into the library and record it.

        Returns the library path (or the original path if the copy failed -
        the run must not lose its clip over a cache problem).
        """
        key = self.clip_key(video_id, segment_start, window)
        filename = f"{video_id}_{int(segment_start)}_{int(window)}{Path(path).suffix}"
        target = self.clips_dir / filename
        try:
            if Path(path) != target:
                shutil.copy2(path, target)
        except OSError as e:
            logger.debug(f"Could not store clip in library: {e}")
            return path

        with self._lock:
            manifest = self._load_manifest()
            manifest['clips'][key] = {
                'video_id': video_id,
                'segment_start': segment_start,
                'window': window,
                'path': str(target),
                'created_at': time.time(),
            }
            self._save_manifest(manifest)
        return str(target)

    # ------------------------------------------------------------------
    # Per-source download stats (prefer videos that actually download)
    # ------------------------------------------------------------------

    def record_result(self, video_id: str, ok: bool) -> None:
        """Record a download success/failure for a source video."""
        with self._lock:
            manifest = self._load_manifest()
            stats = manifest['source_stats'].setdefault(
                video_id, {'ok': 0, 'fail': 0, 'last_ok': None}
            )
            if ok:
                stats['ok'] += 1
                stats['last_ok'] = time.time()
            else:
                stats['fail'] += 1
            self._save_manifest(manifest)

    def success_ratio(self, video_id: str) -> float:
        """Download success ratio for a source video (0.5 when unseen)."""
        with self._lock:
            stats = self._load_manifest()['source_stats'].get(video_id)
        if not stats:
            return 0.5
        total = stats.get('ok', 0) + stats.get('fail', 0)
        if total == 0:
            return 0.5
        return stats.get('ok', 0) / total
