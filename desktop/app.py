"""
ScreenWrite Desktop shell: local Flask server + pywebview window.

    python -m desktop.app          # desktop window (production)
    python -m desktop.app --dev    # server only on :8765, for Vite frontend dev

The server binds 127.0.0.1 on an OS-assigned free port; the pipeline itself
always runs in a child process (see desktop/runner), so this process stays
light and responsive.
"""

import argparse
import logging
import sys
import threading
from pathlib import Path

from desktop.server.app_factory import create_app
from desktop.server.paths import REPO_ROOT, free_port
from desktop.server.runs import RunManager
from desktop.server.settings import SettingsStore

logger = logging.getLogger(__name__)

VO_FILE_TYPES = ('Audio files (*.wav;*.mp3;*.m4a;*.flac;*.ogg)',)
SCRIPT_FILE_TYPES = ('Scripts (*.md;*.markdown;*.txt)',)


class NativeBridge:
    """Exposed to the frontend as window.pywebview.api.*"""

    def __init__(self):
        self._window = None

    def attach(self, window) -> None:
        self._window = window

    def pick_file(self, kind: str):
        """Native file dialog returning a real filesystem path (or None)."""
        import webview

        if self._window is None:
            return None
        if kind == 'script':
            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG, file_types=SCRIPT_FILE_TYPES)
        elif kind == 'vo':
            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG, file_types=VO_FILE_TYPES)
        elif kind == 'fcpxml_save':
            result = self._window.create_file_dialog(
                webview.SAVE_DIALOG, save_filename='timeline.fcpxml')
        elif kind == 'folder':
            result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        else:
            return None

        if not result:
            return None
        return result if isinstance(result, str) else result[0]


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / '.env')
    except ImportError:
        pass


def _serve(app, port: int):
    from werkzeug.serving import make_server

    server = make_server('127.0.0.1', port, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _fatal_dialog(message: str) -> None:
    """Last-resort error surface when the window itself cannot open."""
    if sys.platform.startswith('win'):
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, message, 'ScreenWrite', 0x10)
    else:
        print(message, file=sys.stderr)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='desktop.app')
    parser.add_argument('--dev', action='store_true',
                        help='Run the API server only (port 8765) for frontend dev')
    args = parser.parse_args(argv)

    _load_env()
    settings = SettingsStore()
    run_manager = RunManager(settings)
    app = create_app(run_manager, settings)

    if args.dev:
        logging.basicConfig(level=logging.INFO)
        logger.info('Dev server on http://127.0.0.1:8765 (Vite proxies /api here)')
        app.run(host='127.0.0.1', port=8765, debug=False)
        return 0

    dist_index = Path(__file__).parent / 'frontend' / 'dist' / 'index.html'
    if not dist_index.exists():
        _fatal_dialog(
            'The UI is not built yet.\n\n'
            'Run desktop\\scripts\\create_shortcut.ps1 once (it builds the UI), '
            'or: cd desktop\\frontend && npm install && npm run build'
        )
        return 1

    port = free_port()
    server = _serve(app, port)

    try:
        import webview

        bridge = NativeBridge()
        window = webview.create_window(
            'ScreenWrite',
            f'http://127.0.0.1:{port}',
            js_api=bridge,
            width=1100,
            height=820,
            min_size=(900, 640),
        )
        bridge.attach(window)

        def on_closing():
            if not run_manager.is_active():
                return True
            confirmed = window.create_confirmation_dialog(
                'ScreenWrite',
                'A run is still in progress. Stop it and quit?')
            if confirmed:
                run_manager.cancel()
            return bool(confirmed)

        window.events.closing += on_closing
        webview.start(debug=False)
        return 0
    except Exception as e:  # noqa: BLE001 - surface, don't vanish silently
        _fatal_dialog(
            f'ScreenWrite could not open its window:\n\n{e}\n\n'
            'If this mentions WebView2, install the runtime from:\n'
            'https://developer.microsoft.com/microsoft-edge/webview2/'
        )
        return 1
    finally:
        server.shutdown()


if __name__ == '__main__':
    sys.exit(main())
