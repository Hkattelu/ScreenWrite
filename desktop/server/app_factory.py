"""Flask application factory: API + static SPA serving from frontend/dist."""

from pathlib import Path

from flask import Flask, send_from_directory

from .api import build_api_blueprint

DIST_DIR = Path(__file__).resolve().parents[1] / 'frontend' / 'dist'


def create_app(run_manager, settings) -> Flask:
    app = Flask(__name__, static_folder=None)
    app.register_blueprint(build_api_blueprint(run_manager, settings),
                           url_prefix='/api')

    @app.get('/')
    @app.get('/<path:asset_path>')
    def spa(asset_path: str = 'index.html'):
        target = DIST_DIR / asset_path
        if target.is_file():
            return send_from_directory(DIST_DIR, asset_path)
        # SPA fallback: unknown paths render the app shell.
        return send_from_directory(DIST_DIR, 'index.html')

    return app
