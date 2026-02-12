"""
Full integration flow tests for the asset fetching workflow.

Validates:
- Edit -> Save -> Search -> Select -> Download flow
- Concurrent downloads
- Error recovery
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from flask import Flask, current_app

# Import necessary modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../webapp/backend')))

# Create dummy app
app = Flask(__name__)
app.config['SESSION_FOLDER'] = tempfile.mkdtemp()

class TestFullIntegrationFlow(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = app.config['SESSION_FOLDER']
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_asset_workflow(self):
        """
        Test the complete workflow:
        1. Create session (Edit)
        2. Save Beat (Save)
        3. Search Assets (Search)
        4. Select & Download (Download)
        5. Verify State
        """
        session_id = 'test_session_flow'
        beat_id = 'beat_1'
        
        # 1. Setup initial session state
        session_dir = os.path.join(self.temp_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        initial_state = {
            'sessionId': session_id,
            'beats': [
                {
                    'id': beat_id,
                    'text': 'Initial text',
                    'duration': 5.0,
                    'youtube_search_phrase': 'initial query'
                }
            ],
            'config': {
                'youtube_enabled': True,
                'pexels_enabled': True
            },
            'assets': {}
        }
        
        with open(os.path.join(session_dir, 'state.json'), 'w') as f:
            json.dump(initial_state, f)
            
        # Mock dependencies
        with (
            patch('routes.fetch.get_session_path', return_value=session_dir),
            patch('routes.fetch.session_exists', return_value=True),
            patch('screenwrite.fetchers.asset_orchestrator.AssetOrchestrator.search_assets') as mock_search,
            patch('screenwrite.fetchers.asset_orchestrator.AssetOrchestrator.download_candidate') as mock_download
        ):
            
            from routes.fetch import search_beat_assets, download_beat_asset
            from screenwrite.fetchers.asset_orchestrator import AssetCandidate
            
            # 2. Simulate User Editing & Saving Beat (Update query)
            updated_state = initial_state.copy()
            updated_state['beats'][0]['youtube_search_phrase'] = 'updated query'
            updated_state['beats'][0]['youtube_phrase'] = 'updated query'
            with open(os.path.join(session_dir, 'state.json'), 'w') as f:
                json.dump(updated_state, f)
                
            # 3. Simulate Search (Search endpoint)
            # Mock search results
            mock_search.return_value = [
                AssetCandidate(
                    id='vid_1',
                    title='Test Video 1',
                    thumbnail_url='thumb1.jpg',
                    duration=5.0,
                    source='youtube',
                    metadata={'id': 'vid_1'}
                )
            ]
            
            with app.test_request_context(json={'custom_query': 'custom search'}):
                # Search with a custom query
                response, code = search_beat_assets(session_id, beat_id)
                self.assertEqual(code, 200)
                self.assertEqual(len(response['candidates']), 1)
                
                # Verify orchestrator received the custom query
                mock_search.assert_called()
                call_args = mock_search.call_args[1]
                self.assertEqual(call_args.get('youtube_query'), 'custom search')
                
            # 4. Simulate Download (Download endpoint)
            # Mock successful download path
            downloaded_path = os.path.join(session_dir, 'assets', 'vid_1.mp4')
            mock_download.return_value = downloaded_path
            
            # Let's mock threading.Thread to run immediately for this test
            with patch('threading.Thread') as mock_thread:
                def run_immediately(*args, **kwargs):
                    target = kwargs.get('target')
                    t_args = kwargs.get('args')
                    if target:
                        target(*t_args)
                    return Mock()
                
                mock_thread.side_effect = run_immediately
                
                with app.test_request_context(json={
                    'candidate_id': 'vid_1',
                    'source': 'youtube',
                    'metadata': {'title': 'Test Video 1'},
                    'update_beat_query': True  # User chose to save the search term
                }):
                    # Update request json
                    from flask import request
                    request.json['metadata']['query_used'] = 'custom search'
                    
                    response, code = download_beat_asset(session_id, beat_id)
                    self.assertEqual(code, 200)
                    self.assertEqual(response['success'], True)
                    
                    # 5. Verify State
                    with open(os.path.join(session_dir, 'state.json'), 'r') as f:
                        final_state = json.load(f)
                    
                    # Verify asset is saved
                    self.assertIn(beat_id, final_state['assets'])
                    self.assertEqual(final_state['assets'][beat_id], downloaded_path)
                    
                    # Verify download progress is complete
                    self.assertEqual(final_state['download_progress'][beat_id]['status'], 'complete')
                    
                    # Verify beat query was updated
                    self.assertEqual(final_state['beats'][0]['youtube_phrase'], 'custom search')
                    self.assertEqual(final_state['beats'][0]['youtube_search_phrase'], 'custom search')

    def test_concurrent_downloads_integration(self):
        """
        Test starting multiple downloads for different beats.
        """
        session_id = 'test_session_concurrent'
        
        # Setup session
        session_dir = os.path.join(self.temp_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        initial_state = {
            'sessionId': session_id,
            'beats': [
                {'id': 'beat_1', 'duration': 5.0},
                {'id': 'beat_2', 'duration': 5.0}
            ],
            'config': {},
            'assets': {}
        }
        
        with open(os.path.join(session_dir, 'state.json'), 'w') as f:
            json.dump(initial_state, f)
            
        with (
            patch('routes.fetch.get_session_path', return_value=session_dir),
            patch('routes.fetch.session_exists', return_value=True),
            patch('screenwrite.fetchers.asset_orchestrator.AssetOrchestrator.download_candidate') as mock_download,
            patch('threading.Thread') as mock_thread
        ):
            
            from routes.fetch import download_beat_asset
            
            # Mock thread to run immediately again
            def run_immediately(*args, **kwargs):
                target = kwargs.get('target')
                t_args = kwargs.get('args')
                if target:
                    target(*t_args)
                return Mock()
            mock_thread.side_effect = run_immediately
            
            mock_download.return_value = '/path/to/asset'
            
            # Start download 1
            with app.test_request_context(json={
                'candidate_id': 'vid_1',
                'source': 'youtube'
            }):
                download_beat_asset(session_id, 'beat_1')
                
            # Start download 2
            with app.test_request_context(json={
                'candidate_id': 'vid_2',
                'source': 'pexels'
            }):
                download_beat_asset(session_id, 'beat_2')
                
            # Verify final state has both
            with open(os.path.join(session_dir, 'state.json'), 'r') as f:
                final_state = json.load(f)
                
            self.assertIn('beat_1', final_state['assets'])
            self.assertIn('beat_2', final_state['assets'])
            self.assertEqual(final_state['download_progress']['beat_1']['status'], 'complete')
            self.assertEqual(final_state['download_progress']['beat_2']['status'], 'complete')

if __name__ == '__main__':
    unittest.main()
