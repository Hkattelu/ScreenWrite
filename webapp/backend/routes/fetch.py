"""
Asset fetching route handler.

Handles triggering background asset downloads.
"""

import os
import json
import logging
import threading
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

# Import from parent screenwrite module
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator
from session_utils import get_session_path, session_exists, load_session_state, save_session_state

fetch_bp = Blueprint('fetch', __name__)
logger = logging.getLogger(__name__)

# Track active tasks
active_tasks = {}

def background_fetch(app, session_id, app_config, session_folder):
    """Background task to fetch assets."""
    with app.app_context():
        # Context setup is tricky in threads, so we reconstruct paths
        session_dir = os.path.join(session_folder, session_id)
        state_file = os.path.join(session_dir, 'state.json')
        log_file = os.path.join(session_dir, 'fetch_debug.log')
        
        # Configure logging for this thread
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
        
        logger.info(f"Starting background fetch for session {session_id}")

        # Reload state to get latest config and beats
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state for background fetch: {e}")
            logger.removeHandler(file_handler)
            return

        config = state.get('config', {})
        beats = state.get('beats', [])
        assets_dir = os.path.join(session_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        
        logger.debug(f"Config: {json.dumps(config, indent=2)}")
        logger.info(f"Output dir: {assets_dir}")
        logger.info(f"Found {len(beats)} beats")

        # Initialize Orchestrator
        try:
            orchestrator = AssetOrchestrator(
                pexels_api_key=config.get('pexels_api_key'),
                output_dir=assets_dir,
                youtube_enabled=config.get('youtube_enabled', True),
                pexels_enabled=config.get('pexels_enabled', True)
            )
            logger.info(f"Orchestrator initialized. Fetchers: {[f.name for f in orchestrator.fetchers]}")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            logger.removeHandler(file_handler)
            return

        # Prepare queries
        queries = []
        skipped_count = 0
        for beat in beats:
            # Skip if explicitly skipped (visual mode 'none') or no keywords
            # The logic in frontend clears keywords for 'none' mode, so check empty strings
            yt_phrase = beat.get('youtube_phrase', '')
            stock_keyword = beat.get('stock_keyword', '')
            
            if not yt_phrase and not stock_keyword:
                skipped_count += 1
                continue
                
            queries.append({
                'id': beat['id'],
                'youtube_query': yt_phrase,
                'stock_query': stock_keyword,
                'duration': beat['duration']
            })
        
        logger.info(f"Prepared {len(queries)} queries. Skipped {skipped_count} beats with no keywords.")

        # Update status to fetching
        state['status'] = 'fetching'
        # Initialize asset map if missing
        if not isinstance(state.get('assets'), dict):
            state['assets'] = {}
            
        # Save initial status
        try:
            save_session_state(session_id, state)
        except Exception as e:
            logger.error(f"Failed to save initial status: {e}")

        # Execute batch fetch
        try:
            logger.info("Starting batch fetch with multiple candidates...")
            results = orchestrator.fetch_assets_batch(queries, max_workers=4, candidates_per_beat=3)
            logger.info(f"Batch fetch returned results for {len(results)} beats")
            
            # Reload state again to ensure we don't overwrite concurrent edits (basic optimism)
            with open(state_file, 'r') as f:
                current_state = json.load(f)
                
            # Update assets map
            # results is {beat_id: [path1, path2, ...]}
            current_state['assets'] = results
            current_state['status'] = 'complete'
            current_state['completedAt'] = datetime.now().isoformat()
            
            # Save final state
            save_session_state(session_id, current_state)
            logger.info("Fetch completed and state saved.")
                
        except Exception as e:

            logger.error(f"Batch fetch failed: {e}", exc_info=True)
            # Try to report error
            try:
                with open(state_file, 'r') as f:
                    err_state = json.load(f)
                err_state['status'] = 'error'
                err_state['error'] = str(e)
                save_session_state(session_id, err_state)
            except:
                pass
        finally:
            active_tasks.pop(session_id, None)
            logger.removeHandler(file_handler)


@fetch_bp.route('/session/<session_id>/fetch/<beat_id>', methods=['POST'])
def refresh_beat_asset(session_id, beat_id):
    """Re-fetch asset for a single beat."""
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    try:
        state = load_session_state(session_id)
        config = state.get('config', {})
        beats = state.get('beats', [])
        
        # Find the specific beat
        beat = next((b for b in beats if b['id'] == beat_id), None)
        if not beat:
            return {'error': 'Beat not found'}, 404

        session_dir = get_session_path(session_id)
        assets_dir = os.path.join(session_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)

        # Initialize Orchestrator
        orchestrator = AssetOrchestrator(
            pexels_api_key=config.get('pexels_api_key'),
            output_dir=assets_dir,
            youtube_enabled=config.get('youtube_enabled', True),
            pexels_enabled=config.get('pexels_enabled', True)
        )

        # Prepare query
        query = {
            'id': beat['id'],
            'youtube_query': beat.get('youtube_phrase', ''),
            'stock_query': beat.get('stock_keyword', ''),
            'duration': beat['duration']
        }

        # Fetch single asset
        # We use a thread to not block, but for a single one it might be fast enough
        # Actually, single fetch is better as a synchronous call for immediate feedback if possible,
        # but the orchestrator might take time (YouTube DL).
        # Let's run it in a thread and update state when done.
        
        def single_fetch():
            try:
                # Fetch multiple candidates for this single beat
                results = orchestrator.fetch_assets(
                    query['youtube_query'], 
                    query['stock_query'], 
                    query['duration'], 
                    count=3,
                    beat_id=beat_id
                )
                # Reload and update
                current_state = load_session_state(session_id)
                if not isinstance(current_state.get('assets'), dict):
                    current_state['assets'] = {}
                current_state['assets'][beat_id] = results
                save_session_state(session_id, current_state)
                logger.info(f"Refreshed {len(results)} assets for beat {beat_id} in session {session_id}")
            except Exception as e:
                logger.error(f"Failed to refresh beat {beat_id}: {e}")

        thread = threading.Thread(target=single_fetch)
        thread.daemon = True
        thread.start()

        return {'success': True, 'message': 'Started refresh'}, 200

    except Exception as e:
        logger.error(f"Error starting refresh for beat {beat_id}: {e}")
        return {'error': f"Failed to start refresh: {str(e)}"}, 500


@fetch_bp.route('/session/<session_id>/fetch', methods=['POST'])
def start_fetch(session_id):
    """Start background asset fetching."""
    if not session_exists(session_id):
        return {'error': 'Session not found'}, 404

    if session_id in active_tasks:
        return {'message': 'Fetch already in progress'}, 200

    # Set status to fetching synchronously to prevent UI race condition
    # where it polls before the thread has a chance to update the state
    try:
        state = load_session_state(session_id)
        state['status'] = 'fetching'
        # Reset assets to empty dict if it's a list or missing, to clear "0 assets" state
        if not isinstance(state.get('assets'), dict):
            state['assets'] = {}
            
        save_session_state(session_id, state)
    except Exception as e:
        logger.error(f"Failed to set initial fetch status: {e}")
        return {'error': 'Failed to initialize fetch'}, 500

    # Start background thread
    # Pass necessary config paths since thread context is detached
    # Also pass the actual app instance for context
    thread = threading.Thread(
        target=background_fetch,
        args=(
            current_app._get_current_object(),
            session_id, 
            current_app.config, 
            current_app.config['SESSION_FOLDER']
        )
    )
    thread.daemon = True
    thread.start()
    
    active_tasks[session_id] = thread
    
    return {'success': True, 'message': 'Started background fetch'}, 200
