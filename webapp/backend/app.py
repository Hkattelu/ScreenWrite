"""
Flask backend for screenwrite web app.

Main entry point for the web API server. Handles file uploads, asset
fetching, and FCPXML generation with real-time progress tracking.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')
app.config['SESSION_FOLDER'] = os.getenv('SESSION_FOLDER', './sessions')

# Ensure upload/session folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SESSION_FOLDER'], exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Register blueprints
from routes.upload import upload_bp
from routes.api import api_bp
from routes.export import export_bp
from routes.fetch import fetch_bp

app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(export_bp, url_prefix='/api')
app.register_blueprint(fetch_bp, url_prefix='/api')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {'status': 'healthy'}, 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return {'error': 'Endpoint not found'}, 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f'Internal server error: {error}')
    return {'error': 'Internal server error'}, 500


if __name__ == '__main__':
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=debug
    )

