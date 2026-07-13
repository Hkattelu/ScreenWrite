"""
Pre-flight checks: everything the Run button depends on, with fix-it hints.

ffmpeg/node/yt-dlp reuse the existing DependencyChecker. Resolve is probed in
a SHORT-LIVED SUBPROCESS because ResolveIntegration's constructor raises when
Resolve isn't running and loading fusionscript into the UI process can hang.
"""

import importlib.util
import json
import subprocess
import time

from screenwrite.utils.dependency_checker import DependencyChecker

from .paths import REPO_ROOT, VENV_PYTHON

_CREATE_NO_WINDOW = 0x08000000  # subprocess.CREATE_NO_WINDOW (win32)

_RESOLVE_CACHE = {'at': 0.0, 'result': None}
_RESOLVE_CACHE_TTL = 5.0


def _key_state(settings, name: str) -> dict:
    value = settings.read_key(name)
    return {'ok': bool(value)}


def probe_resolve(timeout: float = 10.0) -> dict:
    """Ask a child process whether Resolve is reachable with a project open."""
    now = time.monotonic()
    if _RESOLVE_CACHE['result'] is not None and now - _RESOLVE_CACHE['at'] < _RESOLVE_CACHE_TTL:
        return _RESOLVE_CACHE['result']

    try:
        completed = subprocess.run(
            [str(VENV_PYTHON), '-m', 'desktop.runner', '--probe-resolve'],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(REPO_ROOT), creationflags=_CREATE_NO_WINDOW,
        )
        result = json.loads(completed.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        result = {'ok': False, 'error': 'Resolve probe timed out'}
    except (OSError, ValueError, IndexError) as e:
        result = {'ok': False, 'error': f'Resolve probe failed: {e}'}

    _RESOLVE_CACHE.update(at=now, result=result)
    return result


def check_all(settings, include_resolve: bool = True) -> dict:
    """All pre-flight states the UI needs to gate the Run button."""
    checker = DependencyChecker()
    report = {
        'ffmpeg': {'ok': bool(checker.check_ffmpeg())},
        'node': {'ok': bool(checker.check_node_version())},
        # The pipeline imports the yt_dlp MODULE (venv), not a PATH binary -
        # DependencyChecker.check_yt_dlp() would false-negative here.
        'ytdlp': {'ok': importlib.util.find_spec('yt_dlp') is not None},
        'whisper': {'ok': importlib.util.find_spec('faster_whisper') is not None},
        'gemini_key': _key_state(settings, 'GEMINI_API_KEY'),
        'pexels_key': _key_state(settings, 'PEXELS_API_KEY'),
    }
    if include_resolve:
        report['resolve'] = probe_resolve()
    return report


def invalidate_resolve_cache() -> None:
    _RESOLVE_CACHE['result'] = None
