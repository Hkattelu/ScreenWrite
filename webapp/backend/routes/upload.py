"""
File upload route handler.

Handles markdown script uploads, validation, and beat parsing.
"""

import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from session_utils import save_session_state

# Import from parent screenwrite module
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from screenwrite.parsing.script_parser import ScriptParser
from screenwrite.core.beat import Beat

upload_bp = Blueprint('upload', __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'md', 'txt'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/upload/sample', methods=['POST'])
def upload_sample():
    """
    Process the pre-defined sample script for onboarding.
    Returns parsed beats and session ID, similar to upload_script.
    """
    try:
        # Use the example script from the project docs
        sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../docs/DOCUMENTARY_EXAMPLE.md'))
        
        if not os.path.exists(sample_path):
            return {'error': 'Sample script not found'}, 404

        # Create session directory
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(current_app.config['SESSION_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Copy sample to session dir for consistency
        target_path = os.path.join(session_dir, 'sample_script.md')
        with open(sample_path, 'r', encoding='utf-8') as src, open(target_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())

        # Parse script
        parser = ScriptParser()
        # Convert beats to dict for JSON serialization
        beats_data = [
            {
                'id': beat.id,
                'text': beat.text,
                'duration': beat.duration,
                'stock_keyword': beat.stock_keyword,
                'youtube_phrase': beat.youtube_search_phrase,
                'visual_type': beat.visual_type,
                'visual_content': beat.visual_content
            }
            for beat in beats
        ]

        total_duration = sum(beat.duration for beat in beats) if beats else 0

        response = {
            'sessionId': session_id,
            'beats': beats_data,
            'summary': {
                'totalBeats': len(beats),
                'estimatedDuration': total_duration,
                'warnings': []
            }
        }

        # Persist initial state
        from datetime import datetime
        initial_state = {
            'sessionId': session_id,
            'scriptName': 'Sample Script',
            'status': 'initialized',
            'config': {},
            'beats': beats_data,
            'summary': response['summary'],
            'assets': [],
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        save_session_state(session_id, initial_state)

        logger.info(f'Session {session_id} created using sample script')
        return response, 200

    except Exception as e:
        logger.error(f'Sample upload error: {str(e)}', exc_info=True)
        return {'error': f'Sample upload failed: {str(e)}'}, 500


@upload_bp.route('/upload', methods=['POST'])
def upload_script():
    """
    Upload and parse a markdown script file.

    Accepts multipart/form-data with 'file' field containing markdown script.
    Returns parsed beats and session ID.

    Returns:
        {
            'sessionId': str,
            'beats': list[dict],
            'summary': {
                'totalBeats': int,
                'estimatedDuration': float,
                'warnings': list[str]
            }
        }
    """
    try:
        # Validate file presence
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400

        file = request.files['file']

        if file.filename == '':
            return {'error': 'No file selected'}, 400

        if not allowed_file(file.filename):
            return {'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}, 400

        # Create session directory
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(current_app.config['SESSION_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(session_dir, filename)
        file.save(filepath)
        logger.info(f'File saved: {filepath}')

        # Parse script
        parser = ScriptParser()
        beats = parser.parse(filepath)

        if not beats:
            return {
                'error': 'No beats generated from script',
                'suggestions': 'Check that your markdown has proper formatting'
            }, 400

        # Calculate summary
        total_duration = sum(beat.duration for beat in beats) if beats else 0
        warnings = []

        if not beats:
            warnings.append('No beats generated from script')

        # Convert beats to dict for JSON serialization
        beats_data = [
            {
                'id': beat.id,
                'text': beat.text,
                'duration': beat.duration,
                'stock_keyword': beat.stock_keyword,
                'youtube_phrase': beat.youtube_search_phrase,
                'visual_type': beat.visual_type,
                'visual_content': beat.visual_content
            }
            for beat in beats
        ]

        response = {
            'sessionId': session_id,
            'beats': beats_data,
            'summary': {
                'totalBeats': len(beats),
                'estimatedDuration': total_duration,
                'warnings': warnings
            }
        }

        # Persist initial state
        from datetime import datetime
        initial_state = {
            'sessionId': session_id,
            'scriptName': filename,
            'status': 'initialized',
            'config': {},
            'beats': beats_data,
            'summary': response['summary'],
            'assets': [],
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        save_session_state(session_id, initial_state)

        logger.info(f'Session {session_id} created with {len(beats)} beats')
        return response, 200

    except Exception as e:
        logger.error(f'Upload error: {str(e)}', exc_info=True)
        return {'error': f'Upload failed: {str(e)}'}, 500

