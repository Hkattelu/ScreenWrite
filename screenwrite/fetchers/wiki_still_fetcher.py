"""
Wiki still-image fetcher: labeled fallback for game entities with no clip.

When no chapter matches an entity, a labeled still from the game's wiki
(Fandom page image, typically the infobox art) is the next-best source: a
still of the RIGHT boss beats a clip of the WRONG one. The page title acts as
the human-authored label, same principle as chapter markers.

The wiki subdomain is guessed from the game title (e.g. "Dark Souls" ->
darksouls.fandom.com) and verified with one search request; an explicit
subdomain can be supplied when the guess is wrong.
"""

import logging
import re
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .base_fetcher import AssetFetcher
from ..config import FANDOM_API_URL, WIKI_REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

_USER_AGENT = "screenwrite-broll/1.0 (b-roll skeleton tool; single-user)"


def guess_wiki_subdomains(game: str) -> List[str]:
    """Candidate Fandom subdomains for a game title, most likely first."""
    tokens = re.findall(r'[a-z0-9]+', (game or '').lower())
    if not tokens:
        return []
    joined = ''.join(tokens)
    guesses = [joined]
    hyphenated = '-'.join(tokens)
    if hyphenated != joined:
        guesses.append(hyphenated)
    return guesses


class WikiStillFetcher(AssetFetcher):
    """
    Fetches labeled entity stills from a game's Fandom wiki.

    Search queries passed to this fetcher are treated as ENTITY NAMES. Results
    carry the wiki page title and URL as provenance.
    """

    def __init__(self, game: str, output_dir: str = None, wiki_subdomain: Optional[str] = None):
        """
        Initialize the fetcher for one game.

        Args:
            game: Game title (used to guess the wiki subdomain)
            output_dir: Directory to save downloaded stills
            wiki_subdomain: Explicit Fandom subdomain (overrides the guess)
        """
        self.game = game
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir())
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._explicit_subdomain = wiki_subdomain
        self._resolved_subdomain: Optional[str] = None
        self._resolve_attempted = False
        self._resolve_lock = threading.Lock()

    @property
    def name(self) -> str:
        """Return the name of this fetcher."""
        return "WikiStill"

    def _api_url(self, subdomain: str) -> str:
        return FANDOM_API_URL.format(subdomain=subdomain)

    def _query_wiki(self, subdomain: str, entity: str,
                    count: int) -> Optional[List[Dict[str, Any]]]:
        """
        Search one wiki for an entity and return pages with images.

        Returns None when the wiki itself is unreachable (bad subdomain), and
        [] when the wiki answered but nothing matched.
        """
        params = {
            'action': 'query',
            'generator': 'search',
            'gsrsearch': entity,
            'gsrlimit': max(count, 3),
            'prop': 'pageimages|info',
            'piprop': 'original',
            'inprop': 'url',
            'format': 'json',
        }
        try:
            response = requests.get(
                self._api_url(subdomain),
                params=params,
                headers={'User-Agent': _USER_AGENT},
                timeout=WIKI_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as e:
            logger.debug(f"Wiki query failed for {subdomain}.fandom.com: {e}")
            return None

        pages = (data.get('query') or {}).get('pages') or {}
        results = []
        for page in pages.values():
            image = (page.get('original') or {}).get('source')
            if not image:
                continue
            results.append({
                'id': str(page.get('pageid', '')),
                'title': page.get('title', ''),
                'thumbnail_url': image,
                'image_url': image,
                'duration': 0.0,
                'page_url': page.get('fullurl', ''),
                'url': page.get('fullurl', ''),
                'wiki': f"{subdomain}.fandom.com",
                'game': self.game,
                'index': page.get('index', 999),
            })
        results.sort(key=lambda r: r.get('index', 999))
        return results

    def _resolve_subdomain(self, probe_entity: str) -> Optional[str]:
        """Find a working wiki subdomain (explicit first, then guesses)."""
        with self._resolve_lock:
            if self._resolve_attempted:
                return self._resolved_subdomain
            self._resolve_attempted = True

            guesses = ([self._explicit_subdomain] if self._explicit_subdomain else [])
            guesses += guess_wiki_subdomains(self.game)
            for subdomain in guesses:
                if self._query_wiki(subdomain, probe_entity, 1) is not None:
                    self._resolved_subdomain = subdomain
                    logger.info(f"Using game wiki: {subdomain}.fandom.com")
                    return subdomain

            logger.warning(
                f"No reachable Fandom wiki found for '{self.game}' "
                f"(tried: {', '.join(g for g in guesses if g)})"
            )
            return None

    def search(self, query: str, count: int = 3) -> List[Dict[str, Any]]:
        """Search the game wiki for labeled stills of an entity."""
        if not query.strip():
            return []
        subdomain = self._resolved_subdomain or self._resolve_subdomain(query)
        if not subdomain:
            return []
        results = self._query_wiki(subdomain, query, count)
        if results is None:
            return []
        for result in results:
            result['entity'] = query
            result['source_url'] = result.get('page_url', '')
        return results[:count]

    def download_by_id(self,
                       asset_id: str,
                       metadata: dict,
                       target_duration: float = None,
                       progress_callback=None) -> Optional[str]:
        """Download the still image for a search result."""
        image_url = metadata.get('image_url') or metadata.get('thumbnail_url')
        if not image_url:
            return None

        safe_title = re.sub(r'[^A-Za-z0-9_-]+', '_', metadata.get('title', str(asset_id)))[:60]
        extension = Path(image_url.split('?')[0]).suffix.lower() or '.jpg'
        if extension not in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'):
            extension = '.jpg'
        output_path = self.output_dir / f"wikistill_{safe_title}_{asset_id}{extension}"

        try:
            response = requests.get(
                image_url,
                headers={'User-Agent': _USER_AGENT},
                timeout=WIKI_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            output_path.write_bytes(response.content)
        except requests.RequestException as e:
            logger.warning(f"Failed to download wiki still {image_url}: {e}")
            return None

        if progress_callback:
            progress_callback(100, 'finished')
        return str(output_path)

    def fetch(self, query: str, duration: float) -> Optional[str]:
        """Fetch one labeled still for an entity."""
        results = self.search(query, count=1)
        if not results:
            return None
        return self.download_by_id(results[0]['id'], results[0])
