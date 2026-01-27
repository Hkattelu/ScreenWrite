import os
import json
import logging
from flask import current_app

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
    
    # Return default empty state if file doesn't exist
    return {
        'sessionId': session_id,
        'status': 'initialized',
        'config': {},
        'beats': [],
        'assets': []
    }

def save_session_state(session_id, state):
    """Save session state to file."""
    try:
        session_dir = get_session_path(session_id)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)
            
        state_file = os.path.join(session_dir, 'state.json')
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save session state for {session_id}: {str(e)}")
        raise e
