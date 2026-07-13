"""
Settings persistence for the desktop app.

Secrets (API keys) live in the repo-root .env - the same file the CLI reads -
managed through the existing EnvManager. Non-secret defaults live in
~/.screenwrite/desktop_settings.json. The API never returns raw keys, only
masked tails, so the frontend can show "configured" without holding secrets.
"""

import json
import os
import threading
from pathlib import Path
from typing import Optional

import requests

from screenwrite.config import GEMINI_REQUEST_TIMEOUT
from screenwrite.utils.env_manager import EnvManager

from .paths import APP_HOME, REPO_ROOT, default_media_dir

_PLACEHOLDER_VALUES = {'', 'your_api_key_here'}

SECRET_KEYS = ('GEMINI_API_KEY', 'PEXELS_API_KEY')

DEFAULT_SETTINGS = {
    'media_dir': None,        # None -> paths.default_media_dir()
    'whisper_model': None,    # None -> pipeline default (small.en)
    'max_workers': 4,
    'last_game': '',
    'prefer_stock_for_generic': True,
    'use_llm_queries': True,
    'skip_failed_beats': True,
}


def _mask(value: Optional[str]) -> Optional[str]:
    if not value or value in _PLACEHOLDER_VALUES:
        return None
    return f"...{value[-4:]}"


class SettingsStore:
    """Reads/writes app settings; thread-safe for the single-user server."""

    def __init__(self, repo_root: Path = REPO_ROOT, app_home: Path = APP_HOME):
        self.repo_root = Path(repo_root)
        self.app_home = Path(app_home)
        self.settings_path = self.app_home / 'desktop_settings.json'
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Secrets (.env)
    # ------------------------------------------------------------------

    def read_key(self, name: str) -> Optional[str]:
        value = os.getenv(name, '').strip()
        return None if value in _PLACEHOLDER_VALUES else value

    def _write_key(self, name: str, value: str) -> None:
        manager = EnvManager(base_path=self.repo_root)
        manager.ensure_env_exists()
        manager.update_env_key(self.repo_root / '.env', name, value)
        # Make the new key visible to this process (preflight, child runners
        # inherit os.environ).
        os.environ[name] = value

    # ------------------------------------------------------------------
    # Defaults (desktop_settings.json)
    # ------------------------------------------------------------------

    def _load_defaults(self) -> dict:
        merged = dict(DEFAULT_SETTINGS)
        try:
            stored = json.loads(self.settings_path.read_text(encoding='utf-8'))
            merged.update({k: stored[k] for k in DEFAULT_SETTINGS if k in stored})
        except (OSError, ValueError):
            pass
        return merged

    def _save_defaults(self, defaults: dict) -> None:
        self.app_home.mkdir(parents=True, exist_ok=True)
        tmp = self.settings_path.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(defaults, indent=2), encoding='utf-8')
        os.replace(tmp, self.settings_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self) -> dict:
        with self._lock:
            defaults = self._load_defaults()
            if not defaults.get('media_dir'):
                defaults['media_dir'] = str(default_media_dir())
            return {
                'gemini_key': _mask(self.read_key('GEMINI_API_KEY')),
                'pexels_key': _mask(self.read_key('PEXELS_API_KEY')),
                'defaults': defaults,
            }

    def put(self, payload: dict) -> dict:
        with self._lock:
            keys = payload.get('keys') or {}
            if keys.get('gemini'):
                self._write_key('GEMINI_API_KEY', keys['gemini'].strip())
            if keys.get('pexels'):
                self._write_key('PEXELS_API_KEY', keys['pexels'].strip())

            if 'defaults' in payload:
                merged = self._load_defaults()
                merged.update({
                    k: payload['defaults'][k]
                    for k in DEFAULT_SETTINGS if k in payload['defaults']
                })
                self._save_defaults(merged)
        return self.get()


def test_gemini_key(key: str) -> dict:
    """Validate a Gemini key with the free ListModels endpoint."""
    if not key:
        return {'ok': False, 'message': 'No key provided'}
    try:
        response = requests.get(
            'https://generativelanguage.googleapis.com/v1beta/models',
            params={'key': key, 'pageSize': 1},
            timeout=GEMINI_REQUEST_TIMEOUT,
        )
    except requests.RequestException as e:
        return {'ok': False, 'message': f'Network error: {e}'}
    if response.status_code == 200:
        return {'ok': True, 'message': 'Key is valid'}
    detail = ''
    try:
        detail = response.json().get('error', {}).get('message', '')
    except ValueError:
        pass
    return {'ok': False, 'status': response.status_code,
            'message': detail or f'Rejected (HTTP {response.status_code})'}


def test_pexels_key(key: str) -> dict:
    """Validate a Pexels key with a one-result search."""
    if not key:
        return {'ok': False, 'message': 'No key provided'}
    try:
        response = requests.get(
            'https://api.pexels.com/v1/search',
            params={'query': 'nature', 'per_page': 1},
            headers={'Authorization': key},
            timeout=15,
        )
    except requests.RequestException as e:
        return {'ok': False, 'message': f'Network error: {e}'}
    if response.status_code == 200:
        return {'ok': True, 'message': 'Key is valid'}
    return {'ok': False, 'status': response.status_code,
            'message': f'Rejected (HTTP {response.status_code})'}
