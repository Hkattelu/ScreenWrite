"""
Export route handler.

Handles FCPXML generation and file download.
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify, current_app, send_file, send_from_directory
from datetime import datetime

# Import from parent screenwrite module
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from screenwrite.generators.xml_generator import XMLGenerator
from screenwrite.core.beat import Beat

export_bp = Blueprint('export', __name__)
logger = logging.getLogger(__name__)


def get_session_path(session_id):
    """Get the session directory path."""
    return os.path.join(current_app.config['SESSION_FOLDER'], session_id)


def session_exists(session_id):
    """Check if session directory exists."""
    return os.path.isdir(get_session_path(session_id))


def load_session_state(session_id):
    """Load session state from file."""
    state_file = os.path.join(get_session_path(session_id), 'state.json')
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            return json.load(f)
    return None


@export_bp.route('/session/<session_id>/export', methods=['POST'])
def export_fcpxml(session_id):
    """
    Generate and export FCPXML file.

    Request body:
    {
        'filename': str (optional, defaults to 'timeline.fcpxml'),
        'resolveIntegration': bool (optional, defaults to false)
    }

    Returns:
        {
            'fcpxmlPath': str,
            'downloadUrl': str,
            'assetCount': int,
            'duration': float
        }
    """
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    try:
        data = request.get_json() or {}
        state = load_session_state(session_id)

        if not state:
            return {'error': 'Failed to load session'}, 500

        # Get beats from state
        beats_data = state.get('beats', [])
        if not beats_data:
            return {'error': 'No beats in session'}, 400

        # Reconstruct Beat objects from data
        beats = []
        for beat_data in beats_data:
            beat = Beat(
                text=beat_data.get('text', ''),
                duration=beat_data.get('duration', 0),
                stock_keyword=beat_data.get('stock_keyword', ''),
                youtube_phrase=beat_data.get('youtube_phrase', ''),
                header=beat_data.get('header', '')
            )
            beat.id = beat_data.get('id', beat.id)
            beats.append(beat)

        # Get assets if available
        assets = state.get('assets', [])

        # Generate FCPXML
        generator = XMLGenerator()
        output_filename = data.get('filename', 'timeline.fcpxml')
        session_path = get_session_path(session_id)
        output_path = os.path.join(session_path, output_filename)

        # Generate XML
        generator.generate(beats, assets, output_path)

        if not os.path.exists(output_path):
            return {'error': 'Failed to generate FCPXML'}, 500

        # Calculate total duration
        total_duration = sum(beat.duration for beat in beats)

        response = {
            'sessionId': session_id,
            'fcpxmlPath': output_path,
            'downloadUrl': f'/api/session/{session_id}/download/{output_filename}',
            'filename': output_filename,
            'assetCount': len(assets),
            'beatCount': len(beats),
            'estimatedDuration': total_duration,
            'fileSize': os.path.getsize(output_path),
            'generatedAt': datetime.now().isoformat()
        }

        # Update session state
        state['status'] = 'exported'
        state['exportedAt'] = datetime.now().isoformat()
        state_file = os.path.join(session_path, 'state.json')
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f'FCPXML exported for session {session_id}: {output_path}')
        return response, 200

    except Exception as e:
        logger.error(f'Export error for session {session_id}: {str(e)}', exc_info=True)
        return {'error': f'Export failed: {str(e)}'}, 500


@export_bp.route('/session/<session_id>/download/<filename>', methods=['GET'])
def download_file(session_id, filename):
    """Download a file from session directory."""
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    try:
        session_path = get_session_path(session_id)
        file_path = os.path.join(session_path, filename)

        # Security: only allow files in session directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(session_path)):
            return {'error': 'Invalid file path'}, 400

        if not os.path.exists(file_path):
            return {'error': 'File not found'}, 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f'Download error: {str(e)}')
        return {'error': 'Download failed'}, 500

