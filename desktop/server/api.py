"""
JSON API for the desktop frontend. Local-only (the server binds 127.0.0.1),
no CORS on purpose - the UI is served from the same origin.
"""

import logging
import subprocess
import sys
from pathlib import Path

from flask import Blueprint, jsonify, request

from screenwrite.utils.cache import clear_cache

from . import preflight
from .paths import APP_HOME, runs_dir
from .runs import RunBusyError, RunValidationError
from .settings import test_gemini_key, test_pexels_key

logger = logging.getLogger(__name__)


def build_api_blueprint(run_manager, settings) -> Blueprint:
    api = Blueprint('api', __name__)

    # ------------------------------------------------------------------
    # Health / preflight / settings
    # ------------------------------------------------------------------

    @api.get('/health')
    def health():
        return jsonify({'ok': True, 'app': 'screenwrite-desktop'})

    @api.get('/preflight')
    def get_preflight():
        include_resolve = request.args.get('resolve', '1') != '0'
        return jsonify(preflight.check_all(settings, include_resolve=include_resolve))

    @api.get('/settings')
    def get_settings():
        return jsonify(settings.get())

    @api.put('/settings')
    def put_settings():
        return jsonify(settings.put(request.get_json(force=True) or {}))

    @api.post('/settings/test-key')
    def test_key():
        payload = request.get_json(force=True) or {}
        provider = payload.get('provider')
        if provider == 'gemini':
            key = payload.get('key') or settings.read_key('GEMINI_API_KEY')
            return jsonify(test_gemini_key(key))
        if provider == 'pexels':
            key = payload.get('key') or settings.read_key('PEXELS_API_KEY')
            return jsonify(test_pexels_key(key))
        return jsonify({'ok': False, 'message': f'Unknown provider: {provider}'}), 422

    # ------------------------------------------------------------------
    # Script loading (native dialog supplies a real path)
    # ------------------------------------------------------------------

    @api.post('/script/load')
    def load_script():
        payload = request.get_json(force=True) or {}
        path = Path(payload.get('path') or '')
        if not path.is_file():
            return jsonify({'error': f'File not found: {path}'}), 422
        try:
            text = path.read_text(encoding='utf-8', errors='replace')
        except OSError as e:
            return jsonify({'error': f'Could not read file: {e}'}), 422
        return jsonify({'text': text, 'path': str(path)})

    # ------------------------------------------------------------------
    # Runs
    # ------------------------------------------------------------------

    @api.post('/run')
    def start_run():
        payload = request.get_json(force=True) or {}
        try:
            run_id = run_manager.start(payload)
        except RunBusyError as e:
            return jsonify({'error': str(e)}), 409
        except RunValidationError as e:
            return jsonify({'error': str(e)}), 422
        return jsonify({'run_id': run_id})

    @api.get('/run/current')
    def current_run():
        after_seq = request.args.get('after_seq', 0, type=int)
        return jsonify(run_manager.snapshot(after_seq=after_seq))

    @api.post('/run/<run_id>/cancel')
    def cancel_run(run_id):
        cancelled = run_manager.cancel(run_id)
        return jsonify({'cancelled': cancelled})

    @api.get('/run/<run_id>/result')
    def run_result(run_id):
        result = run_manager.result(run_id)
        if result is None:
            return jsonify({'error': 'No result for this run'}), 404
        return jsonify(result)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @api.post('/reveal')
    def reveal():
        payload = request.get_json(force=True) or {}
        path = Path(payload.get('path') or '')
        if not path.exists():
            return jsonify({'error': f'Path not found: {path}'}), 422
        if sys.platform.startswith('win'):
            subprocess.Popen(['explorer', '/select,', str(path)])
        else:
            subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open',
                              str(path.parent)])
        return jsonify({'ok': True})

    @api.post('/cache/clear')
    def cache_clear():
        if run_manager.is_active():
            return jsonify({'error': 'Cannot clear caches during a run'}), 409
        clear_cache()
        return jsonify({'ok': True})

    @api.get('/app-info')
    def app_info():
        return jsonify({
            'app_home': str(APP_HOME),
            'runs_dir': str(runs_dir()),
        })

    return api
