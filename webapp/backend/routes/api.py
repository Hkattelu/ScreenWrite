"""
Core API routes for workflow management.

Handles session configuration, beat updates, and status queries.
"""

import os
import logging
from flask import Blueprint, request, jsonify, send_from_directory
from datetime import datetime
from session_utils import get_session_path, session_exists, load_session_state, save_session_state

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


@api_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session state."""
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    try:
        state = load_session_state(session_id)
        return state, 200
    except Exception as e:
        logger.error(f'Error loading session {session_id}: {str(e)}')
        return {'error': 'Failed to load session'}, 500


@api_bp.route('/session/<session_id>/config', methods=['PUT'])
def update_config(session_id):
    """Update session configuration."""
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    try:
        data = request.get_json()
        state = load_session_state(session_id)

        # Update config
        if 'youtubeEnabled' in data:
            state['config']['youtube_enabled'] = data['youtubeEnabled']
        if 'pexelsEnabled' in data:
            state['config']['pexels_enabled'] = data['pexelsEnabled']
        if 'pexelsApiKey' in data:
            state['config']['pexels_api_key'] = data['pexelsApiKey']
        if 'outputDir' in data:
            state['config']['output_dir'] = data['outputDir']

        state['status'] = 'configured'
        state['updatedAt'] = datetime.now().isoformat()

        save_session_state(session_id, state)
        return {'success': True}, 200

    except Exception as e:
        logger.error(f'Error updating config for {session_id}: {str(e)}')
        return {'error': 'Failed to update config'}, 500


@api_bp.route('/session/<session_id>/beats', methods=['PUT'])
def update_beats(session_id):
    """Update beats for a session."""
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    try:
        data = request.get_json()
        state = load_session_state(session_id)

        if 'beats' not in data:
            return {'error': 'No beats provided'}, 400

        state['beats'] = data['beats']
        state['updatedAt'] = datetime.now().isoformat()

        save_session_state(session_id, state)
        return {'success': True}, 200

    except Exception as e:
        logger.error(f'Error updating beats for {session_id}: {str(e)}')
        return {'error': 'Failed to update beats'}, 500


@api_bp.route('/session/<session_id>/status', methods=['GET'])
def get_status(session_id):
    """Get session processing status."""
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    try:
        state = load_session_state(session_id)
        assets = state.get('assets', {})
        
        # Count non-null assets if it's a dict, otherwise count length if list
        if isinstance(assets, dict):
            asset_count = sum(1 for path in assets.values() if path)
        else:
            asset_count = len(assets)

        return {
            'sessionId': session_id,
            'status': state.get('status', 'unknown'),
            'beatCount': len(state.get('beats', [])),
            'assetCount': asset_count
        }, 200

    except Exception as e:
        logger.error(f'Error getting status for {session_id}: {str(e)}')
        return {'error': 'Failed to get status'}, 500


@api_bp.route('/session/<session_id>/media/<filename>', methods=['GET'])
def get_media(session_id, filename):
    """Serve a media file from the session assets directory."""
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    try:
        session_path = get_session_path(session_id)
        assets_path = os.path.join(session_path, 'assets')
        
        if not os.path.exists(assets_path):
            return {'error': 'Assets directory not found'}, 404

        return send_from_directory(assets_path, filename)
    except Exception as e:
        logger.error(f'Error serving media {filename} for {session_id}: {str(e)}')
        return {'error': 'Failed to serve media'}, 500


@api_bp.route('/session/<session_id>/delete', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session and all associated data."""
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    try:
        import shutil
        session_path = get_session_path(session_id)
        shutil.rmtree(session_path)
        logger.info(f'Session {session_id} deleted')
        return {'success': True}, 200

    except Exception as e:
        logger.error(f'Error deleting session {session_id}: {str(e)}')
        return {'error': 'Failed to delete session'}, 500