"""
Routes for Simple B-Roll mode.
Provides direct search and download without session management.
"""

import os
import logging
from flask import Blueprint, request, send_file
from pathlib import Path
import tempfile
import shutil

# Import from parent screenwrite module
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate

simple_broll_bp = Blueprint('simple_broll', __name__)
logger = logging.getLogger(__name__)

# Temporary directory for simple b-roll downloads
SIMPLE_BROLL_DIR = Path(tempfile.gettempdir()) / "simple_broll"
SIMPLE_BROLL_DIR.mkdir(parents=True, exist_ok=True)

@simple_broll_bp.route('/simple-broll/search', methods=['POST'])
def search_simple_broll():
    """Search for videos for simple b-roll."""
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        
        if not query:
            return {'error': 'Query is required'}, 400
            
        # Initialize Orchestrator
        orchestrator = AssetOrchestrator(
            pexels_api_key=os.getenv('PEXELS_API_KEY'),
            output_dir=None,
            youtube_enabled=True,
            pexels_enabled=True
        )
        
        # Search for candidates
        candidates = orchestrator.search_assets(
            youtube_query=query,
            stock_query=query,
            duration=10.0, # Default target duration for search
            count=10
        )
        
        candidates_json = [c.to_dict() for c in candidates]
        
        return {
            'success': True,
            'candidates': candidates_json,
            'query': query
        }, 200
        
    except Exception as e:
        logger.error(f"Simple B-Roll search failed: {e}", exc_info=True)
        return {'error': str(e)}, 500

@simple_broll_bp.route('/simple-broll/download', methods=['POST'])
def download_simple_broll():
    """Download a specific segment of a video."""
    try:
        data = request.get_json() or {}
        candidate_data = data.get('candidate')
        start_time = float(data.get('start_time', 0))
        duration = float(data.get('duration', 5))
        
        if not candidate_data:
            return {'error': 'Candidate data is required'}, 400
            
        candidate = AssetCandidate(
            id=candidate_data.get('id'),
            title=candidate_data.get('title'),
            thumbnail_url=candidate_data.get('thumbnail_url'),
            duration=candidate_data.get('duration'),
            source=candidate_data.get('source'),
            metadata=candidate_data.get('metadata')
        )
        
        # Initialize Orchestrator with our temp dir
        orchestrator = AssetOrchestrator(
            pexels_api_key=os.getenv('PEXELS_API_KEY'),
            output_dir=str(SIMPLE_BROLL_DIR),
            youtube_enabled=True,
            pexels_enabled=True
        )
        
        # Download segment
        file_path = orchestrator.download_segment(
            candidate,
            start_time=start_time,
            duration=duration
        )
        
        if not file_path or not os.path.exists(file_path):
            return {'error': 'Download failed'}, 500
            
        # Return the file directly
        # We might want to use a more descriptive name for the download
        filename = Path(file_path).name
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"broll_{filename}"
        )
        
    except Exception as e:
        logger.error(f"Simple B-Roll download failed: {e}", exc_info=True)
        return {'error': str(e)}, 500
