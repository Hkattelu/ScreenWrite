"""
Chaptered-gameplay asset fetcher: entity -> human-labeled chapter -> clip.

This is the primary source for game-entity beats. Instead of searching YouTube
with narration keywords, it searches for chaptered walkthrough corpora ("all
bosses", "all cutscenes", "100% walkthrough") for the script's game, reads the
chapter markers a human already authored (via yt-dlp metadata - no YouTube
Data API needed), and fuzzy-matches the beat's extracted entity against those
chapter titles. A hit yields ground-truth "what's on screen" without any
visual understanding.

Candidate variety is cheap by design: when a chapter matches, the 2-3
candidates are different start offsets within (and across) matching chapters,
and clips are cut with a loose window rather than the tight beat duration, so
the editor can slide the in-point past walk-up/menu moments.
"""

import logging
import re
import threading
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

try:
    from rapidfuzz import fuzz as _rapidfuzz
except ImportError:
    _rapidfuzz = None

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

from .base_fetcher import AssetFetcher
from .youtube_client import YouTubeClient
from ..config import (
    CHAPTER_SOURCE_QUERY_TEMPLATES,
    CHAPTER_SEARCH_RESULTS_PER_QUERY,
    CHAPTER_MAX_SOURCE_VIDEOS,
    CHAPTER_MIN_CHAPTERS,
    CHAPTER_MIN_SOURCE_DURATION,
    CHAPTER_MATCH_THRESHOLD,
    CHAPTER_OFFSET_STEP_SECONDS,
    CHAPTER_WINDOW_MIN_SECONDS,
    CHAPTER_WINDOW_SLACK_SECONDS,
)

logger = logging.getLogger(__name__)


def normalize_title(text: str) -> str:
    """Lowercase and strip punctuation so chapter labels compare cleanly."""
    text = (text or '').lower()
    text = re.sub(r'[^a-z0-9 ]+', ' ', text)
    return ' '.join(text.split())


def chapter_match_score(entity: str, chapter_title: str) -> float:
    """
    Score (0-100) how well an entity name matches a chapter title.

    Uses rapidfuzz token_set_ratio when available; otherwise a difflib-based
    fallback that treats token-subset containment as a full match (chapter
    titles decorate entity names with noise like "(Boss Fight)").
    """
    entity_norm = normalize_title(entity)
    title_norm = normalize_title(chapter_title)
    if not entity_norm or not title_norm:
        return 0.0

    if entity_norm in title_norm:
        return 100.0

    entity_tokens = set(entity_norm.split())
    title_tokens = set(title_norm.split())
    if entity_tokens and entity_tokens.issubset(title_tokens):
        return 100.0

    if _rapidfuzz is not None:
        return float(_rapidfuzz.token_set_ratio(entity_norm, title_norm))

    ratio = SequenceMatcher(None, entity_norm, title_norm).ratio() * 100
    token_overlap = len(entity_tokens & title_tokens) / max(1, len(entity_tokens)) * 100
    return max(ratio, token_overlap)


def clip_window_seconds(beat_duration: float) -> float:
    """Loose download window for a beat: duration + slack, with a floor."""
    return max(CHAPTER_WINDOW_MIN_SECONDS, beat_duration + CHAPTER_WINDOW_SLACK_SECONDS)


class ChapteredGameplayFetcher(AssetFetcher):
    """
    Fetches gameplay clips for named game entities from chaptered walkthroughs.

    Search queries passed to this fetcher are treated as ENTITY NAMES (e.g.
    "Bell Gargoyles"), not narration text. The chapter index for the game is
    built lazily on first search and reused for every beat in the run.
    """

    def __init__(self, game: str, output_dir: str = None,
                 youtube_client: Optional[YouTubeClient] = None,
                 library=None):
        """
        Initialize the fetcher for one game.

        Args:
            game: Game title the script is about (e.g. "Dark Souls")
            output_dir: Directory for downloaded clips
            youtube_client: Existing YouTubeClient to reuse for downloads
            library: Optional GameLibrary for persistent chapter-index and
                clip reuse across runs (fetch the game's footage once, ever)
        """
        self.game = game
        self.youtube_client = youtube_client or YouTubeClient(output_dir=output_dir)
        self.library = library
        self._chapter_index: Optional[List[Dict[str, Any]]] = None
        self._index_lock = threading.Lock()
        self._download_cache: Dict[str, Optional[str]] = {}
        self._download_lock = threading.Lock()

    @property
    def name(self) -> str:
        """Return the name of this fetcher."""
        return "ChapteredGameplay"

    # ------------------------------------------------------------------
    # Chapter index (built once per run, shared across beats/threads)
    # ------------------------------------------------------------------

    def _flat_search(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Flat YouTube search (no per-video metadata)."""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'socket_timeout': 20,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{count}:{query}", download=False)
        return [e for e in (info.get('entries') or []) if e and e.get('id')]

    def _fetch_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full metadata (including chapters) for one video."""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'socket_timeout': 30,
        }
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            logger.warning(f"Failed to fetch metadata for {video_id}: {e}")
            return None

    def _title_mentions_game(self, title: str) -> bool:
        """True if all tokens of the game name appear in the video title."""
        game_tokens = set(normalize_title(self.game).split())
        title_tokens = set(normalize_title(title).split())
        return bool(game_tokens) and game_tokens.issubset(title_tokens)

    def _build_chapter_index(self) -> List[Dict[str, Any]]:
        """
        Discover chaptered source videos for the game and collect their chapters.

        Returns a list of source dicts:
        {video_id, title, url, thumbnail_url, duration, chapters: [...]}
        """
        if yt_dlp is None:
            logger.error("yt-dlp not available, cannot build chapter index")
            return []

        # 1. Flat-search each corpus query and pool unique, plausible sources.
        seen_ids = set()
        pool: List[Dict[str, Any]] = []
        for template in CHAPTER_SOURCE_QUERY_TEMPLATES:
            query = template.format(game=self.game)
            try:
                entries = self._flat_search(query, CHAPTER_SEARCH_RESULTS_PER_QUERY)
            except Exception as e:
                logger.warning(f"Chapter source search failed for '{query}': {e}")
                continue
            for entry in entries:
                vid = entry['id']
                if vid in seen_ids:
                    continue
                seen_ids.add(vid)
                duration = entry.get('duration') or 0
                if duration and duration < CHAPTER_MIN_SOURCE_DURATION:
                    continue
                if not self._title_mentions_game(entry.get('title', '')):
                    continue
                pool.append(entry)

        # 2. Fetch full metadata (chapters) for the longest sources first -
        #    long walkthroughs are the richest labeled corpora.
        pool.sort(key=lambda e: e.get('duration') or 0, reverse=True)
        index: List[Dict[str, Any]] = []
        for entry in pool[:CHAPTER_MAX_SOURCE_VIDEOS]:
            info = self._fetch_video_info(entry['id'])
            if not info:
                continue
            chapters = info.get('chapters') or []
            if len(chapters) < CHAPTER_MIN_CHAPTERS:
                continue
            thumbnails = info.get('thumbnails') or []
            index.append({
                'video_id': info.get('id', entry['id']),
                'title': info.get('title', ''),
                'url': f"https://www.youtube.com/watch?v={info.get('id', entry['id'])}",
                'thumbnail_url': thumbnails[-1].get('url', '') if thumbnails else '',
                'duration': info.get('duration') or 0,
                'chapters': chapters,
            })

        total_chapters = sum(len(s['chapters']) for s in index)
        logger.info(
            f"Chapter index for '{self.game}': {len(index)} source videos, "
            f"{total_chapters} chapters"
        )
        return index

    def get_chapter_index(self) -> List[Dict[str, Any]]:
        """Return the chapter index, building it on first use (thread-safe).

        With a game library attached, the index persists across runs and is
        only rebuilt after its TTL expires.
        """
        with self._index_lock:
            if self._chapter_index is None:
                library = getattr(self, 'library', None)
                if library is not None:
                    self._chapter_index = library.load_chapter_index()
                if self._chapter_index is None:
                    self._chapter_index = self._build_chapter_index()
                    if library is not None and self._chapter_index:
                        library.save_chapter_index(self._chapter_index)
            return self._chapter_index

    # ------------------------------------------------------------------
    # Entity -> candidates
    # ------------------------------------------------------------------

    def match_chapters(self, entity: str) -> List[Dict[str, Any]]:
        """
        Fuzzy-match an entity against every chapter in the index.

        Returns matches sorted best-first:
        {score, video_id, video_title, video_url, thumbnail_url,
         chapter_title, chapter_start, chapter_end}
        """
        matches = []
        for source in self.get_chapter_index():
            for chapter in source['chapters']:
                score = chapter_match_score(entity, chapter.get('title', ''))
                if score < CHAPTER_MATCH_THRESHOLD:
                    continue
                start = float(chapter.get('start_time') or 0)
                end = float(chapter.get('end_time') or 0)
                if end <= start:
                    end = start + 3 * CHAPTER_OFFSET_STEP_SECONDS + CHAPTER_WINDOW_MIN_SECONDS
                matches.append({
                    'score': score,
                    'video_id': source['video_id'],
                    'video_title': source['title'],
                    'video_url': source['url'],
                    'thumbnail_url': source['thumbnail_url'],
                    'chapter_title': chapter.get('title', ''),
                    'chapter_start': start,
                    'chapter_end': end,
                })
        # At equal match quality, prefer source videos that have actually
        # downloaded successfully before (YouTube hard-blocks some streams).
        library = getattr(self, 'library', None)
        if library is not None:
            matches.sort(key=lambda m: (-m['score'], -library.success_ratio(m['video_id'])))
        else:
            matches.sort(key=lambda m: -m['score'])
        return matches

    def search(self, query: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Search for candidate clips for an ENTITY (query is the entity name).

        Candidates are diversified across matching chapters first, then across
        start offsets within each chapter (the multi-offset variety trick).

        Returns candidate metadata dicts; 'id' encodes video and offset.
        """
        if yt_dlp is None:
            logger.error("yt-dlp not available, cannot search chaptered gameplay")
            return []
        if not query.strip():
            return []

        matches = self.match_chapters(query)
        if not matches:
            logger.info(f"No chapter match for entity '{query}' ({self.game})")
            return []

        # Round-robin: offset 0 of every matched chapter, then offset 1, etc.
        candidates: List[Dict[str, Any]] = []
        offset_round = 0
        window = CHAPTER_WINDOW_MIN_SECONDS
        while len(candidates) < count:
            emitted = False
            for match in matches:
                if len(candidates) >= count:
                    break
                offset = offset_round * CHAPTER_OFFSET_STEP_SECONDS
                segment_start = match['chapter_start'] + offset
                # Keep the whole window inside the chapter - except offset 0,
                # which is always allowed (a short chapter of the RIGHT thing
                # beats no candidate at all).
                if offset_round > 0 and segment_start + window > match['chapter_end']:
                    continue
                candidates.append({
                    'id': f"{match['video_id']}@{int(segment_start)}",
                    'title': (f"{match['chapter_title']} "
                              f"[{self._format_ts(segment_start)}] - {match['video_title']}"),
                    'thumbnail_url': match['thumbnail_url'],
                    'duration': window,
                    'url': match['video_url'],
                    'video_id': match['video_id'],
                    'game': self.game,
                    'entity': query,
                    'chapter_title': match['chapter_title'],
                    'chapter_start': match['chapter_start'],
                    'chapter_end': match['chapter_end'],
                    'segment_start': segment_start,
                    'match_score': match['score'],
                    'source_url': f"{match['video_url']}&t={int(segment_start)}",
                })
                emitted = True
            if not emitted:
                break
            offset_round += 1

        return candidates

    @staticmethod
    def _format_ts(seconds: float) -> str:
        """Format seconds as h:mm:ss / m:ss for human-readable labels."""
        seconds = int(seconds)
        hours, rem = divmod(seconds, 3600)
        minutes, secs = divmod(rem, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    # ------------------------------------------------------------------
    # Downloads (delegated to YouTubeClient's ranged section download)
    # ------------------------------------------------------------------

    def download_by_id(self,
                       asset_id: str,
                       metadata: dict,
                       target_duration: float = None,
                       progress_callback=None) -> Optional[str]:
        """
        Download the candidate's segment window.

        The window is loose on purpose: beat duration + slack (floored), so the
        editor can slide the in-point without re-fetching.
        """
        segment_start = float(metadata.get('segment_start', metadata.get('chapter_start', 0)))
        window = clip_window_seconds(target_duration or 0)
        return self.download_segment(
            asset_id, metadata,
            start_time=segment_start,
            duration=window,
            progress_callback=progress_callback,
        )

    def download_segment(self,
                         asset_id: str,
                         metadata: dict,
                         start_time: float,
                         duration: float,
                         progress_callback=None) -> Optional[str]:
        """
        Download [start_time, start_time + duration] of the source video.

        Checked in order: this run's in-memory cache, the persistent game
        library, then the network. Successful downloads are stored back into
        the library and per-source success stats are recorded either way.
        """
        video_id = metadata.get('video_id') or str(asset_id).split('@')[0]
        video_url = metadata.get('url', f"https://www.youtube.com/watch?v={video_id}")
        end_time = start_time + duration

        cache_key = f"{video_id}@{int(start_time)}+{int(duration)}"
        with self._download_lock:
            if cache_key in self._download_cache:
                return self._download_cache[cache_key]

        library = getattr(self, 'library', None)
        path = library.find_clip(video_id, start_time, duration) if library else None
        if path:
            logger.info(f"Clip served from game library: {cache_key}")
        else:
            path = self.youtube_client.download_section(
                video_url,
                start_time=start_time,
                end_time=end_time,
                tag=f"{self.game}_{metadata.get('entity', video_id)}_{int(start_time)}",
                progress_callback=progress_callback,
            )
            if library is not None:
                library.record_result(video_id, ok=path is not None)
                if path:
                    path = library.store_clip(path, video_id, start_time, duration)

        with self._download_lock:
            self._download_cache[cache_key] = path
        return path

    def fetch(self, query: str, duration: float) -> Optional[str]:
        """Fetch one clip for an entity (search + download best candidate)."""
        results = self.fetch_multi(query, duration, count=1)
        return results[0] if results else None

    def fetch_multi(self, query: str, duration: float, count: int = 3) -> List[str]:
        """Fetch multiple candidate clips for an entity."""
        paths = []
        for candidate in self.search(query, count=count):
            path = self.download_by_id(candidate['id'], candidate, target_duration=duration)
            if path:
                paths.append(path)
        return paths
